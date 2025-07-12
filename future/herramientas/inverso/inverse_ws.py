# FUNCIÓN QUE DEFINE EL SYMBOL SEGUN EL EXCHANGE
# ----------------------------------------------
def definir_symbol(exchange, symbol):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        if exchange == "BINANCE":
            symbol = symbol + "USD_PERP"
        
        if exchange.upper() == "BYBIT":
            symbol = symbol + "USD"
        
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
        print("PRECIO ACTUAL INVERSE_WS ABIERTO")
        print("")

        # Variables globales
        global precio_actual
        
        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)
        
        # BINANCE
        if exchange == "BINANCE":
            import binance_inverse_ws
            import binance_inverse
            import threading
            
            precio_actual = binance_inverse.precio_actual_activo(symbol)
            hilo_precio_actual = threading.Thread(target=binance_inverse_ws.precio_actual_activo,args=(symbol,))
            hilo_precio_actual.daemon = True
            hilo_precio_actual.start()
            
            while True:
                precio_actual = binance_inverse_ws.precio_actual
                if precio_actual == None:
                    precio_actual = binance_inverse.precio_actual_activo(symbol)
                
                if not(hilo_precio_actual.is_alive()):
                    hilo_precio_actual = threading.Thread(target=binance_inverse_ws.precio_actual_activo,args=(symbol,))
                    hilo_precio_actual.daemon = True
                    hilo_precio_actual.start()
                #print(precio_actual)

        # BYBIT
        if exchange == "BYBIT":
            import bybit_inverse
            import bybit_inverse_ws
            import threading
            
            precio_actual = bybit_inverse.precio_actual_activo(symbol)
            hilo_precio_actual = threading.Thread(target=bybit_inverse_ws.precio_actual_activo,args=(symbol,))
            hilo_precio_actual.daemon = True
            hilo_precio_actual.start()
            
            while True:
                precio_actual = bybit_inverse_ws.precio_actual
                if precio_actual == None:
                    precio_actual = bybit_inverse.precio_actual_activo(symbol)
                
                if not(hilo_precio_actual.is_alive()):
                    hilo_precio_actual = threading.Thread(target=bybit_inverse_ws.precio_actual_activo,args=(symbol,))
                    hilo_precio_actual.daemon = True
                    hilo_precio_actual.start()
                #print(precio_actual)
    
    except Exception as e:
        print(f"ERROR EN LA FUNCIÓN: inverse_ws.precio_actual_activo()")
        print(e)
        print("PRECIO ACTUAL FUTURE_WS CERRADO")
        print("")
#--------------------------------------------------------

#precio_actual_activo("bybit","op")