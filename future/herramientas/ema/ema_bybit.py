from pybit.unified_trading import HTTP
import numpy as np
import asyncio
import json
import time

# Sesión pública
bybit_session = HTTP(
                    testnet=False,
                    api_key="1XJt60yrfh4sSwU45Q",
                    api_secret="GyQyHOe8SRKje2g4WN7JxEZrfIqy0sOqtjdP",
                    )

# FUNCIÓN QUE OBTINE LAS EMAs DE BYBIT
# ------------------------------------
def obtener_ema(symbol: str, interval: str = "1", periodo: int = 9, vela: int = 1) -> float:
    """
    Obtiene la EMA de un símbolo en Bybit de forma ligera y rápida.

    Parámetros:
        symbol (str): Ej. "BTCUSDT"
        interval (str): Intervalo de velas ("1","5","15","60","D", etc.)
        periodo (int): Periodo de la EMA (ej. 9, 21, 50...)
        vela (int): Índice de la vela (1 = última, 2 = penúltima, etc.)

    Retorna:
        float: Valor de la EMA en la vela especificada
    """
    try:
    
        # warm-up amplio para mayor exactitud
        need = periodo + vela + 1
        limit = max(need, 5 * periodo)
        kl = bybit_session.get_kline(category="linear", symbol=symbol, interval=interval, limit=limit)
        kl = kl.get("result", {}).get("list", [])
        kl.sort(key=lambda x: int(x[0]))
        
        closes = np.array([float(k[4]) for k in kl], dtype=float)

        if len(closes) < (periodo + vela):
            raise ValueError(f"Velas insuficientes: {len(closes)} < {periodo + vela}")

        # EMA precisa (semilla = SMA de las primeras N)
        alpha = 2.0 / (periodo + 1.0)
        ema = np.empty_like(closes)
        ema[:] = np.nan
        first = periodo - 1
        ema[first] = closes[:periodo].mean()
        for i in range(first + 1, len(closes)):
            ema[i] = closes[i] * alpha + ema[i - 1] * (1.0 - alpha)

        return(float(ema[-vela]))

    except Exception as e:
        print(f"\nError obteniendo EMA: {e}")
        return None
# ------------------------------------

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        
        # Precio actual en BYBIT
        precio = float(bybit_session.get_public_trade_history(category="linear",symbol=symbol,limit=1,)['result']['list'][0]['price'])
        return precio
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BYBIT")
        print(e)
        print("")
        return None
#--------------------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol, orderId=""):
    try:
        return bybit_session.get_open_orders(category="linear",symbol=symbol,orderId=orderId)["result"]['list']

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BYBIT")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCION QUE MODIFICA UAN ORDEN
#--------------------------------------------------------
def modificar_orden(symbol, orderId, order_type="", quantity="", price="", side=""):
    try:

        # Definir el lado para el modo hedge
        positionSide = 0
        if side.upper() == "BUY":
            positionSide = 1
            side =side[0] + side[1:].lower()
        if side.upper() == "SELL":
            positionSide = 2
            side =side[0] + side[1:].lower()
        
        # Coloca la orden "LIMIT"
        order = bybit_session.amend_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType=order_type,
            qty=quantity,
            price=price,
            timeinforce="GTC",
            positionIdx=positionSide,
            orderId = orderId
            )

        order = obtener_ordenes(symbol, order["result"]["orderId"])
        #print(json.dumps(order,indent=2))
        
        if order_type.upper() == "CONDITIONAL":
            price = float(order[0]["triggerPrice"])
        else:
            price = float(order[0]["price"])
        
        print(f"\nOrden {order_type.upper()}-{side} de {order[0]['qty']} {symbol.split('USDT')[0]}  modificada en {price}. ID:", order[0]["orderId"])
        
        return {
                "orderId": order[0]["orderId"],
                "price": price,
                "qty": float(order[0]["qty"])
                }
    
    except Exception as e:
        print(f"\nERROR MODIFICANDO LA ORDEN EN BYBIT\n{e}")
# ---------------------------------------------------

emas = []
ema_cercana = ""
# EMA AUTOMATICA
# --------------
async def ema_auto(symbol, tipo):
    global ema_cercana, emas
    ema_dinamica = ""
    while True:
        try:
            # Reiniciar la lista de emas
            # --------------------------
            if emas == []:
                for temp in ["M", "W", "D", "240", "60", "15", "5", "1"]:
                    ema9 = obtener_ema(symbol, temp, 9, 1)
                    if ema9 != None:
                        emas.append(
                                {
                                "periodo": 9,
                                "temporalidad": temp,
                                "precio": ema9, 
                                "orderId": "", 
                                "orderPrice": "",
                                "colocada": False, 
                                "ejecutada": False
                                }
                                )
                    ema54 = obtener_ema(symbol, temp, 54, 1)
                    if ema54 != None:
                        emas.append(
                                {
                                "periodo": 54,
                                "temporalidad": temp,
                                "precio": ema54, 
                                "orderId": "", 
                                "orderPrice": "",
                                "colocada": False, 
                                "ejecutada": False
                                }
                                )
            # --------------------------
            
            # Obtener la ema mas cercana al precio
            # ------------------------------------
            precio_actual = precio_actual_activo(symbol)
            distancia = 1
            ema_mas_cercana = ""
            ema_siguiente = ""
            for ema in emas:
                
                # Actualizar la lista de ema
                # --------------------------
                precio_ema_actual = obtener_ema(symbol, ema['temporalidad'], ema['periodo'], 1)
                if precio_ema_actual != None:
                    ema['precio'] = precio_ema_actual
                # --------------------------

                # Buscar la ema mas cercana
                # -------------------------
                if abs(precio_actual-ema['precio'])/precio_actual < distancia:
                    if tipo.upper() == "LONG" and ema['precio'] < precio_actual:
                        ema_mas_cercana = ema
                        distancia = abs(precio_actual-ema['precio'])/precio_actual
                        if distancia > 1/100:
                            ema_siguiente = ema
                    if tipo.upper() == "SHORT" and ema['precio'] > precio_actual:
                        ema_mas_cercana = ema
                        distancia = abs(precio_actual-ema['precio'])/precio_actual
                        if distancia > 1/100:
                            ema_siguiente = ema
                # -------------------------        
            # ------------------------------------
            print("EMA MAS CERCANA", json.dumps(ema_mas_cercana, indent=2))
            print("EMA SIGUIENTE", json.dumps(ema_siguiente, indent=2))

            # Corretear la orden
            # ------------------
            for ema in emas:
                if ema['orderId'] != "" and ema['colocada'] and not ema['ejecutada']:
                    ema_dinamica = ema

            if ema_dinamica != "":
                precio_ema_actual = obtener_ema(symbol, ema_dinamica['temporalidad'], ema_dinamica['periodo'], 1)
                
                if tipo.upper() == "LONG" and precio_ema_actual > ema_dinamica['orderPrice']:
                    #cancelar_orden(symbol, ema_dinamica['orderId'])
                    ema_cercana['precio'] = precio_ema_actual
                
                if tipo.upper() == "SHORT" and precio_ema_actual < ema_dinamica['orderPrice']:
                    #cancelar_orden(symbol, ema_dinamica['orderId'])
                    ema_cercana['precio'] = precio_ema_actual
            # ------------------

            await asyncio.sleep(0.1)
    
        except Exception as e:
            print(f"\nERROR EN LA FUNCION ema_auto()\n{e}")
            await asyncio.sleep(0.1)
# --------------

# --- Ejemplo ---
#print("EMA9 última vela:", obtener_ema("XNYUSDT", "M", 9, 1))
#symbol = "BTCUSDT"
#asyncio.run(ema_auto("MYXUSDT", "SHORT"))
#modificar_orden("CTSIUSDT", "796db398-6a05-41ca-a883-a3f37d750923", price=0.1)

async def tarea1():
    print("Tarea 1 iniciada")
    await asyncio.sleep(2)
    print("Tarea 1 terminda")

async def tarea2():
    print("Tarea 2 iniciada")
    await asyncio.sleep(3)
    print("Tarea 2 terminada")

async def tarea3():
    print("Tarea 3 iniciada")
    await asyncio.sleep(5)
    print("Tarea 3 terminada")

async def main():
    task1 = asyncio.create_task(tarea1())
    task2 = asyncio.create_task(tarea2())
    task3 = asyncio.create_task(tarea3())
    await asyncio.gather(task1, task2, task3)

asyncio.run(main())