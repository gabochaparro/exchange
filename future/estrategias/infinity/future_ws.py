# FUNCIÓN QUE DEFINE EL SYMBOL SEGUN EL EXCHANGE
# ----------------------------------------------
def definir_symbol(exchange, symbol):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        if exchange == "BINANCE" or exchange.upper() == "BYBIT":
            symbol = symbol + "USDT"
        
        if exchange == "BITGET":
            symbol = symbol + "USDT_UMCBL"

        if exchange == "BINGX":
            symbol = symbol + "-USDT"

        if exchange == "OKX":
            symbol = symbol + "-USDT-SWAP"
        
        if exchange == "KUCOIN":
            if symbol == "BTC":
                symbol = "XBT"
            symbol = symbol + "USDTM"
        
        if exchange == "GATEIO":
            symbol = symbol + "_USDT"
 
        print( f"{exchange} - {symbol}\n")
        return symbol
    
    except Exception as e:
        print("ERROR EN LA DEFICIÓN DEL SÍMBOLO\n")
# ----------------------------------------------

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
precio_actual = None
def precio_actual_activo(exchange, symbol):
    try:
        print("PRECIO ACTUAL FUTURE_WS ABIERTO\n")
        
        # Variables globales
        global precio_actual
        
        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)
        
        # BINANCE
        if exchange == "BINANCE":
            import binance_websocket.binance_ws as binancews
            import binance_
            import threading
            import time
            import asyncio

            # Clase y funcion para iniciar websocket
            ClasePrecioActual = binancews.PreciosActuales()
            def iniciar_ws():
                asyncio.run(ClasePrecioActual.precio_actual_activo("f", symbol))

            # Iniciar variables e hilo
            precio_actual = binance_.precio_actual_activo(symbol)
            hilo_precio_actual = threading.Thread(target=iniciar_ws, daemon=True)
            hilo_precio_actual.start()

            ti = time.time()
            while True:
                try:
                    # Consultar precio actual
                    precio_actual = ClasePrecioActual.precio_actual.get(symbol)
                    if precio_actual == None:
                        precio_actual = binance_.precio_actual_activo(symbol)
                        print("API", precio_actual)
                        time.sleep(3.6)
                    
                    # Verificar que el hilo esta vivo
                    if not(hilo_precio_actual.is_alive()):
                        precio_actual = binance_.precio_actual_activo(symbol)
                        hilo_precio_actual = threading.Thread(target=iniciar_ws, daemon=True)
                        hilo_precio_actual.start()

                    #consultar la API cada cierto tiempo
                    if (time.time() - ti) > 3.6:
                        precio_ahora = binance_.precio_actual_activo(symbol)
                        if abs(precio_actual-precio_ahora)/precio_ahora > 0.1/100:
                            precio_actual = precio_ahora
                            print("API", precio_actual)
                        ti = time.time()
                    
                    #print(precio_actual)
                    
                except Exception as e:
                    print(f"ERROR EN EL BUCLE DE LA FUNCIÓN: future_ws.precio_actual_activo()\n")
                    print(e)

        # BYBIT
        if exchange == "BYBIT":
            import bybit_websocket.bybit_ws as bybitws
            import bybit
            import threading
            import time
            import asyncio

            # Clase Precio Actual y funcion iniciar_ws
            ClasePresioActual = bybitws.PreciosActuales()
            def iniciar_ws():
                asyncio.run(ClasePresioActual.precio_actual_activo("linear", [symbol]))
            
            # Iniciar variables e hilo
            precio_actual = bybit.precio_actual_activo(symbol)
            hilo_precio_actual = threading.Thread(target=iniciar_ws, daemon=True)
            hilo_precio_actual.start()
            
            ti = time.time()
            while True:
                try:
                    # Consultar precio actual
                    precio_actual = ClasePresioActual.precios_actuales.get(symbol)
                    if precio_actual == None:
                        precio_actual = bybit.precio_actual_activo(symbol)
                        print("API", precio_actual)
                        time.sleep(3.6)
                    
                    # Verificar que el hilo esta vivo
                    if not(hilo_precio_actual.is_alive()):
                        precio_actual = bybit.precio_actual_activo(symbol)
                        hilo_precio_actual = threading.Thread(target=iniciar_ws, daemon=True)
                        hilo_precio_actual.start()

                    # Consultar la API cada cierto tiempo
                    if(time.time() - ti) > 3.6:
                        precio_ahora = bybit.precio_actual_activo(symbol)
                        if abs(precio_actual-precio_ahora)/precio_ahora > 0.1/100:
                            precio_actual = precio_ahora
                            print("API", precio_actual)
                        ti = time.time()
                    
                    #print(precio_actual)

                except Exception as e:
                    print(f"ERROR EN EL BUCLE DE LA FUNCIÓN: future_ws.precio_actual_activo()\n")
                    print(e)
    
    except Exception as e:
        print(f"ERROR EN LA FUNCIÓN: future_ws.precio_actual_activo()")
        print(e)
        print("PRECIO ACTUAL FUTURE_WS CERRADO\n")
#--------------------------------------------------------

#precio_actual_activo("BYBIT", "BTC")