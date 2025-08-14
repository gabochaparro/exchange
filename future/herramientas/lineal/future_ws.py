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
 
        print("")
        print( exchange, "-", symbol)
        print("")
        return symbol
    
    except Exception as e:
        print("ERROR EN LA DEFICIÓN DEL SÍMBOLO")
# ----------------------------------------------

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
precio_actual = None
def precio_actual_activo(exchange, symbol):
    try:
        print("PRECIO ACTUAL FUTURE_WS ABIERTO")
        print("")
        
        # Variables globales
        global precio_actual
        
        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)
        
        # BINANCE
        if exchange == "BINANCE":
            import binance_ws
            import binance_
            import threading
            import time

            # Iniciar variables e hilo
            precio_actual = binance_.precio_actual_activo(symbol)
            hilo_precio_actual = threading.Thread(target=binance_ws.precio_actual_activo,args=(symbol,))
            hilo_precio_actual.daemon = True
            hilo_precio_actual.start()

            ti = time.time()
            while True:
                # Consultar precio actual
                precio_actual = binance_ws.precio_actual
                if precio_actual == None:
                    precio_actual = binance_.precio_actual_activo(symbol)
                
                # Verificar que el hilo esta vivo
                if not(hilo_precio_actual.is_alive()):
                    precio_actual = binance_.precio_actual_activo(symbol)
                    hilo_precio_actual = threading.Thread(target=binance_ws.precio_actual_activo,args=(symbol,))
                    hilo_precio_actual.daemon = True
                    hilo_precio_actual.start()
                #print(precio_actual)

                #consultar la API cada cierto tiempo
                if (time,time() - ti) > 3.6:
                    precio_ahora = binance_.precio_actual_activo(symbol)
                    if abs(precio_actual-precio_ahora)/precio_ahora > 0.1/100:
                        precio_actual = precio_ahora
                        if not(hilo_precio_actual.is_alive()):
                            hilo_precio_actual = threading.Thread(target=binance_ws.precio_actual_activo,args=(symbol,))
                            hilo_precio_actual.daemon = True
                            hilo_precio_actual.start()
                    precio_actual = precio_ahora
                    ti = time.time()

        # BYBIT
        if exchange == "BYBIT":
            import bybit_ws
            import bybit
            import threading
            import time

            # Iniciar variables e hilo
            precio_actual = bybit.precio_actual_activo(symbol)
            hilo_precio_actual = threading.Thread(target=bybit_ws.precio_actual_activo,args=(symbol,))
            hilo_precio_actual.daemon = True
            hilo_precio_actual.start()
            
            ti = time.time()
            while True:
                # Consultar precio actual
                precio_actual = bybit_ws.precio_actual
                if precio_actual == None:
                    precio_actual = bybit.precio_actual_activo(symbol)
                
                # Verificar que el hilo esta vivo
                if not(hilo_precio_actual.is_alive()):
                    precio_actual = bybit.precio_actual_activo(symbol)
                    hilo_precio_actual = threading.Thread(target=bybit_ws.precio_actual_activo,args=(symbol,))
                    hilo_precio_actual.daemon = True
                    hilo_precio_actual.start()
                #print(precio_actual)

                # Consultar la API cada cierto tiempo
                if(time.time() - ti) > 3.6:
                    precio_ahora = bybit.precio_actual_activo(symbol)
                    if abs(precio_actual-precio_ahora)/precio_ahora > 0.1/100:
                        precio_actual = precio_ahora
                        if not(hilo_precio_actual.is_alive()):
                            hilo_precio_actual = threading.Thread(target=bybit_ws.precio_actual_activo,args=(symbol,))
                            hilo_precio_actual.daemon = True
                            hilo_precio_actual.start()
                    precio_actual = precio_ahora
                    ti = time.time()
    
    except Exception as e:
        print(f"ERROR EN LA FUNCIÓN: future_ws.precio_actual_activo()")
        print(e)
        print("PRECIO ACTUAL FUTURE_WS CERRADO")
        print("")
#--------------------------------------------------------