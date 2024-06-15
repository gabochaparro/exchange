import binance_
import bybit
import bitget
import bingx
import okx_
import kucoin
import gateio
import json
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
 
        return symbol
    
    except Exception as e:
        print("ERROR EN LA DEFICIÓN DEL SÍMBOLO")
# ----------------------------------------------

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(exchange, symbol):
    try:
        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)
        print("")
        print( exchange, "-", symbol)
        print("")
        
        # BINANCE
        if exchange == "BINANCE":
            precio = binance_.precio_actual_activo(symbol)

        # BYBIT
        if exchange == "BYBIT":
            precio = bybit.precio_actual_activo(symbol)

        # BITGET
        if exchange == "BITGET":
            precio = bitget.precio_actual_activo(symbol)    

        # BINGX
        if exchange == "BINGX":
            precio = bingx.precio_actual_activo(symbol)

        # OKX
        if exchange == "OKX":
            precio = okx_.precio_actual_activo(symbol)

        # KUCOIN
        if exchange == "KUCOIN":
            precio = kucoin.precio_actual_activo(symbol)

        # GATEIO
        if exchange == "GATEIO":
            precio = gateio.precio_actual_activo(symbol)

        return precio
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol}")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN UNIVERSAL QUE CREA UNA ORDEN LIMITI Ó MARKET
#-----------------------------------------------------
def nueva_orden(exchange, symbol, order_type, quantity, price, side, leverage):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()
        order_type = order_type.upper()
        side = side.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)
        
        # BINANCE
        if exchange == "BINANCE":
            binance_.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # BYBIT
        if exchange == "BYBIT":
            bybit.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # BITGET
        if exchange == "BITGET":
            bitget.nueva_orden(symbol, order_type, quantity, price, side, leverage)    

        # BINGX
        if exchange == "BINGX":
            bingx.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # OKX
        if exchange == "OKX":
            okx_.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # KUCOIN
        if exchange == "KUCOIN":
            kucoin.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # GATEIO
        if exchange == "GATEIO":
            gateio.nueva_orden(symbol, order_type, quantity, price, side, leverage)

    except Exception as e:
        print("ERROR CREANDO LA ORDEN")
        print(e)
        print("")
#-----------------------------------------------------

#print(precio_actual_activo(exchange="okx", symbol="BTC"))
print("")
