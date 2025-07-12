# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#----------------------------------------------
precio_actual = None
def precio_actual_activo(symbol):
    try:
        import websocket
        import json
        import ssl
        import binance_inverse
        
        global precio_actual
        precio_actual = binance_inverse.precio_actual_activo(symbol)
        
        def on_message(ws, message):
            global precio_actual
            data = json.loads(message)
            #print(json.dumps(data, indent=2))
            precio_actual = float(data['p'])
            #print(precio_actual)

        def on_error(ws, error):
            global precio_actual
            precio_actual = binance_inverse.precio_actual_activo(symbol)
            print("### Error en el WS BINANCE: Precio Actual ###:", error)
            print("")

        def on_close(ws, close_status_code, close_msg):
            global precio_actual
            precio_actual = binance_inverse.precio_actual_activo(symbol)
            print("### WS BINANCE: Precio actual Cerrado ###")
            print("")

        def on_open(ws):
            global precio_actual
            precio_actual = binance_inverse.precio_actual_activo(symbol)
            print("### WS BINANCE: Precio Actual Abierto ###")
            print("")
        
        websocket_url = f"wss://dstream.binance.com/ws/{symbol.lower()}@aggTrade"
        
        ws = websocket.WebSocketApp(
                                    websocket_url,
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close
                                    )
        
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    
    except Exception as e:
        precio_actual = binance_inverse.precio_actual_activo(symbol)
        print("ERROR EN LA FUNCIÓN: binance_inverse_ws.precio_actual_activo()")
        print(e)
        print("")
#----------------------------------------------

#precio_actual_activo("BTCUSD_PERP")