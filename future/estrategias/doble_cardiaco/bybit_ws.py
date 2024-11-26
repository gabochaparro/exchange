import websocket
import json
import ssl
import time
import threading


# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#----------------------------------------------
precio_actual = 0
def precio_actual_activo(symbol):
    try:
        
        topic = f"publicTrade.{symbol}"

        def on_message(ws, message):
            global precio_actual, data_precio_actual
            data_precio_actual = json.loads(message)
            #print(json.dumps(data,indent=2))
            precio_actual = float(data_precio_actual['data'][0]['p'])

        def on_error(ws, error):
            print("### Error en el WS BYBIT: Precio Actual ###:", error)
            print(json.dumps(data_precio_actual,indent=2))

        def on_close(ws, close_status_code, close_msg):
            print("### WS BYBIT: Precio actual Cerrado ###")

        def on_open(ws):
            print("### WS BYBIT: Precio Actual Abierto ###")
            ws.send(json.dumps({"op": "subscribe", "args": [topic]}))

        ws = websocket.WebSocketApp(url="wss://stream.bybit.com/v5/public/linear",
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
        
        def ping():
            while True:
                time.sleep(20)
                ws.send(json.dumps({'op': 'ping'}))
                print("Ping Enviado")
        
        threading.Thread(target=ping).start()
        
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    except Exception as e:
        print("ERROR BUSCANDO PRECIO ACTUAL EN BYBIT")
        print(e)
        print("")
#----------------------------------------------
