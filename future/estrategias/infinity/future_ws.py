import binance_ws
import bybit_ws
import bybit
import threading
import time


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
precio_actual = 0
def precio_actual_activo(exchange, symbol):
    try:
        # Variables globales
        global precio_actual
        
        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)
        
        # BINANCE
        if exchange == "BINANCE":
            threading.Thread(target=binance_ws.precio_actual_activo,args=(symbol,)).start()
            while True:
                precio_actual = binance_ws.precio_actual
                if precio_actual == 0:
                    time.sleep(3)
                    precio_actual = binance_ws.precio_actual
                    if precio_actual == 0:
                        threading.Thread(target=binance_ws.precio_actual_activo,args=(symbol,)).start()
                #print(precio_actual)

        # BYBIT
        if exchange == "BYBIT":
            threading.Thread(target=bybit_ws.precio_actual_activo,args=(symbol,)).start()
            while True:
                precio_actual = bybit_ws.precio_actual
                if precio_actual == 0:
                    time.sleep(9)
                    precio_actual = bybit_ws.precio_actual
                    if precio_actual == 0:
                        precio_actual = bybit.precio_actual_activo(symbol)
                        threading.Thread(target=bybit_ws.precio_actual_activo,args=(symbol,)).start()
                #print(precio_actual)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol}")
        print(e)
        print("")
        return 0
#--------------------------------------------------------