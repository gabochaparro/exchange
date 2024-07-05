import websocket
import json
import ssl
import threading
import time

symbol = "btcusdt"

def precio_actual_activo(symbol):
    global precio
    precio = 0

    def on_message(ws, message):
        global precio
        precio = float(json.loads(message)['p'])

    def on_error(ws, error):
        print(error)

    def on_close(ws, close_status_code, close_msg):
        print("### closed ###")

    def on_open(ws):
        print("### opened ###")
    websocket_url = f"wss://fstream.binance.com/ws/{symbol}@aggTrade"
    ws = websocket.WebSocketApp(websocket_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


# SUBPROCESO precio_actual_activo
# Crear un subproceso para el stop loss buy
hilo_precio_actual_activo = threading.Thread(target=precio_actual_activo, args=(symbol,))
# Establecer el subproceso como demonio para que se detenga cuando se cierre el programa principal
hilo_precio_actual_activo.daemon = True
# Iniciar el subproceso
hilo_precio_actual_activo.start()

while True:
    if not hilo_precio_actual_activo.is_alive():
        # SUBPROCESO precio_actual_activo
        # Crear un subproceso para el stop loss buy
        hilo_precio_actual_activo = threading.Thread(target=precio_actual_activo, args=(symbol,))
        # Establecer el subproceso como demonio para que se detenga cuando se cierre el programa principal
        hilo_precio_actual_activo.daemon = True
        # Iniciar el subproceso
        hilo_precio_actual_activo.start()

    #time.sleep(2)
    print(precio)