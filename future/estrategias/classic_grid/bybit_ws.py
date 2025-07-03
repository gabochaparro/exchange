# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#----------------------------------------------
precio_actual = None
def precio_actual_activo(symbol):
    try:
        import websocket
        import json
        import ssl
        import time
        import threading
        from pybit.unified_trading import HTTP# Definir la session para Bybit
        import bybit
        
        global precio_actual
        precio_actual = bybit.precio_actual_activo(symbol)
        topic = f"publicTrade.{symbol}"

        def on_message(ws, message):
            global precio_actual, data_precio_actual
            data_precio_actual = json.loads(message)
            #print(json.dumps(data_precio_actual,indent=2))
            
            # Recibir mensaje de Pong
            if "ret_msg" in data_precio_actual:
                if data_precio_actual['ret_msg'] == "pong":
                    #print("Pong Recibido")
                    #print("")
                    pass
            
            # Recibir el mensaje del precio actual
            if "data" in data_precio_actual:
                precio_actual = float(data_precio_actual['data'][0]['p'])
                #time.sleep(1)
                #print(precio_actual)

        def on_error(ws, error):
            global precio_actual
            precio_actual = bybit.precio_actual_activo(symbol)
            print("### Error en el WS BYBIT: Precio Actual ###:", error)

        def on_close(ws, close_status_code, close_msg):
            global precio_actual
            precio_actual = bybit.precio_actual_activo(symbol)
            print("### WS BYBIT: Precio actual Cerrado ###")

        def on_open(ws):
            global precio_actual
            precio_actual = bybit.precio_actual_activo(symbol)
            ws.send(json.dumps({"op": "subscribe", "args": [topic]}))
            print("### WS BYBIT: Precio Actual Abierto ###")

        ws = websocket.WebSocketApp(
                                    url="wss://stream.bybit.com/v5/public/linear",
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close
                                    )
        
        def ping():
            while True:
                time.sleep(36)
                ws.send(json.dumps({'op': 'ping'}))
                #print("Ping Enviado")

        threading.Thread(target=ping).start()
        
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    except Exception as e:
        print("ERROR BUSCANDO PRECIO ACTUAL EN BYBIT")
        print(e)
        print("")
#----------------------------------------------

#precio_actual_activo("BTCUSDT")