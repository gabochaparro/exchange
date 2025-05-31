import websocket
import json
import ssl


# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#----------------------------------------------
precio_actual = 0
def precio_actual_activo(symbol):
    try:
        
        def on_message(ws, message):
            global precio_actual
            data = json.loads(message)
            #print(json.dumps(data, indent=2))
            precio_actual = float(data['p'])
            #print(precio_actual)

        def on_error(ws, error):
            print("### Error en el WS BINANCE: Precio Actual ###:", error)

        def on_close(ws, close_status_code, close_msg):
            print("### WS BINANCE: Precio actual Cerrado ###")

        def on_open(ws):
            print("### WS BINANCE: Precio Actual Abierto ###")
        
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
        print("ERROR BUSCANDO PRECIO ACTUAL EN BINANCE")
        print(e)
        print("")
#----------------------------------------------

#precio_actual_activo("BTCUSD_PERP")