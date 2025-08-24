import json
import threading
import time
import requests
from collections import OrderedDict
from datetime import datetime

import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import websocket

# -----------------------------
# CONFIG
# -----------------------------
SYMBOL = "API3USDT"     # Perpetuos USDT en Bybit (linear)
INTERVAL = "1"         # 1 minuto
CATEGORY = "linear"    # spot | linear | inverse | option
WS_URL = f"wss://stream.bybit.com/v5/public/{CATEGORY}"
REST_KLINE = "https://api.bybit.com/v5/market/kline"

# Guardamos velas en un buffer indexado por 'start' (ms). Evita duplicados y concat.
bars_lock = threading.Lock()
bars = OrderedDict()   # key: start (int ms) -> dict con ohlcv + confirm

# -----------------------------
# HELPERS
# -----------------------------
def ms_to_dt(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000)

def seed_history(limit=200):
    """
    Carga histórico inicial por REST para que el gráfico no arranque vacío.
    Solo guarda velas confirmadas.
    """
    params = {
        "category": CATEGORY,
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "limit": str(limit)
    }
    r = requests.get(REST_KLINE, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    # En v5, data["result"]["list"] es una lista de listas con OHLCV (orden temporal inverso)
    # Documentación oficial: /v5/market/kline. :contentReference[oaicite:1]{index=1}
    result = data.get("result", {})
    klines = result.get("list", []) or []
    # Cada item suele ser: [start, open, high, low, close, volume, turnover] (strings salvo start)
    # Orden: último primero -> invertimos para ordenar ascendente
    for row in reversed(klines):
        try:
            start = int(row[0])
            o = float(row[1]); h = float(row[2]); l = float(row[3]); c = float(row[4]); v = float(row[5])
        except Exception:
            continue
        with bars_lock:
            bars[start] = {
                "start": start,
                "time": ms_to_dt(start),
                "open": o, "high": h, "low": l, "close": c, "volume": v,
                "confirm": True  # histórico viene cerrado
            }

def build_dataframe(include_unconfirmed=True) -> pd.DataFrame:
    with bars_lock:
        rows = list(bars.values())
    if not rows:
        return pd.DataFrame(columns=["time","open","high","low","close","volume","confirm"])
    df = pd.DataFrame(rows, columns=["time","open","high","low","close","volume","confirm"])
    df = df.dropna().sort_values("time").reset_index(drop=True)

    if not include_unconfirmed:
        df = df[df["confirm"]]

    return df

# -----------------------------
# WEBSOCKET
# -----------------------------
def on_open(ws):
    print("✅ Conectado WS. Subscribiendo kline...")
    sub = {"op": "subscribe", "args": [f"kline.{INTERVAL}.{SYMBOL}"]}
    ws.send(json.dumps(sub))

def on_message(ws, message):
    msg = json.loads(message)
    # Esperamos: { topic:"kline.1.SYMBOL", type:"snapshot|delta", data:[{start, end, interval, open, close, high, low, volume, turnover, confirm, timestamp}], ts:... }
    # Doc oficial kline WS v5. :contentReference[oaicite:2]{index=2}
    data = msg.get("data")
    if not isinstance(data, list):
        return

    updates = []
    for k in data:
        # Filtra mensajes incompletos
        required = ("start","open","high","low","close","volume")
        if not all(key in k for key in required):
            continue
        try:
            start = int(k["start"])
            o = float(k["open"]); h = float(k["high"]); l = float(k["low"]); c = float(k["close"]); v = float(k["volume"])
            confirm = bool(k.get("confirm", False))
        except Exception:
            continue
        updates.append((start, o, h, l, c, v, confirm))

    if not updates:
        return

    with bars_lock:
        for start, o, h, l, c, v, confirm in updates:
            # Insertar o reemplazar la vela por su 'start'. Así evitamos duplicados.
            bars[start] = {
                "start": start,
                "time": ms_to_dt(start),
                "open": o, "high": h, "low": l, "close": c, "volume": v,
                "confirm": confirm
            }
        # Limitar tamaño del buffer para no crecer sin límite
        if len(bars) > 2000:
            # Keep últimos 2000
            keys = list(bars.keys())[-2000:]
            bars_copy = OrderedDict((k, bars[k]) for k in keys)
            bars.clear()
            bars.update(bars_copy)

def on_error(ws, err):
    print("⚠️ WS error:", err)

def on_close(ws, *_):
    print("🔌 WS cerrado. Reconectando en 3s...")
    time.sleep(3)
    start_ws_thread()

def ws_loop():
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    # ping_interval ayuda a mantener la conexión viva
    ws.run_forever(ping_interval=20, ping_timeout=10)

def start_ws_thread():
    t = threading.Thread(target=ws_loop, daemon=True)
    t.start()

# -----------------------------
# DASH APP
# -----------------------------
app = Dash(__name__)
app.layout = html.Div([
    html.H1(f"📈 Panel Bybit - {SYMBOL} ({INTERVAL}m)", style={"textAlign": "center"}),
    dcc.Graph(id="live-graph", animate=False),
    dcc.Interval(id="graph-update")
])

@app.callback(
    Output("live-graph", "figure"),
    Input("graph-update", "n_intervals")
)
def update_graph(_):
    df = build_dataframe(include_unconfirmed=True)
    if df.empty:
        return go.Figure()

    fig = go.Figure()

    # Velas confirmadas
    fig.add_trace(go.Candlestick(
        x=df["time"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    ))

    # Última vela
    last_row = df.iloc[-1]
    precio_actual = last_row["close"]
    tiempo_actual = last_row["time"]

    if not last_row["confirm"]:
        # Determinar color según tendencia
        color_vela = "#00CC96" if last_row["close"] >= last_row["open"] else "#EF553B"

        # Vela en curso con mismo esquema de colores
        fig.add_trace(go.Candlestick(
            x=[tiempo_actual],
            open=[last_row["open"]],
            high=[last_row["high"]],
            low=[last_row["low"]],
            close=[last_row["close"]],
            increasing_line_color=color_vela,
            decreasing_line_color=color_vela,
            name=str(precio_actual)
        ))

        # ➖ Línea punteada horizontal desde la vela en curso hasta el eje derecho
        fig.add_shape(
            type="line",
            x0=0,    # inicio en la vela actual (último valor del eje x)
            x1=1,    # borde derecho (columna de precios)
            y0=precio_actual,
            y1=precio_actual,
            line=dict(color=color_vela, width=0.5, dash="dot"),
            xref="x domain",   # clave: mezcla vela → borde derecho
            yref="y"
        )

        # 📍 Etiqueta de precio actual en el eje derecho
        fig.add_annotation(
            xref="paper",
            x=1.04,
            y=precio_actual,
            text=f"{precio_actual:.4f}",
            showarrow=False,
            font=dict(color="white", size=12),
            bgcolor=color_vela,
        )

    # Layout
    fig.update_layout(
        xaxis=dict(rangeslider=dict(visible=False)),
        yaxis=dict(side="right"),
        template="plotly_dark",
        margin=dict(l=10, r=80, t=40, b=10),
        uirevision="constant"
    )

    return fig

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    # 1) Histórico inicial (evita gráfico vacío y da contexto)
    try:
        seed_history(limit=300)
        print("📚 Histórico inicial cargado.")
    except Exception as e:
        print("⚠️ No se pudo cargar el histórico inicial:", e)

    # 2) WS en segundo plano
    start_ws_thread()

    # 3) Arrancar Dash
    app.run(debug=True, port=8050)
