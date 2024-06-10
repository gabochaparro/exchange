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
            symbol = symbol + "USDTM"
        
        if exchange == "GATEIO":
            symbol = symbol + "_USDT"
 
        return symbol
    
    except Exception as e:
        print("ERROR EN LA DEFICIÓN DEL SÍMBOLO")
# ----------------------------------------------

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

#nueva_orden(exchange="okx", symbol="ordi", order_type="LIMIT", quantity=0.1, price=56, side="buy", leverage=50)

