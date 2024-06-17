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
 
        print("")
        print( exchange, "-", symbol)
        print("")
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
        
        # Mensaje
        print(f"Colocando orden {side}-{order_type} de {symbol} en {exchange}...")
        print(f"cantidad: {quantity}, precio: {price}, apalancamiento: {leverage}")
        print("")

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

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(exchange, symbol): 
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            binance_.cancelar_ordenes(symbol=symbol)
        
        # BYBIT
        if exchange == "BYBIT":
            bybit.cancelar_ordenes(symbol=symbol)
        
        # BITGET
        if exchange == "BITGET":
            bitget.cancelar_ordenes(symbol=symbol)
        
        # BINGX
        if exchange == "BINGX":
            bingx.cancelar_ordenes(symbol=symbol)
        
        # OKX
        if exchange == "OKX":
            okx_.cancelar_ordenes(symbol=symbol)
        
        # KUCOIN
        if exchange == "KUCOIN":
            kucoin.cancelar_ordenes(symbol=symbol)
        
        # GATEIO
        if exchange == "GATEIO":
            gateio.cancelar_ordenes(symbol=symbol)
        
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN QUE BUSCA LA INFO DE TODAS LAS ORDENES ABIERTAS
# -------------------------------------------------------
def obtener_ordenes(exchange, symbol):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            return binance_.obtener_ordenes(symbol=symbol)

        # BYBIT
        if exchange == "BYBIT":
            return bybit.obtener_ordenes(symbol=symbol)

        # BITGET
        if exchange == "BITGET":
            return bitget.obtener_ordenes(symbol=symbol)

        # BINGX
        if exchange == "BINGX":
            return bingx.obtener_ordenes(symbol=symbol)

        # OKX
        if exchange == "OKX":
            return okx_.obtener_ordenes(symbol=symbol)

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.obtener_ordenes(symbol=symbol)

        # GATEIO
        if exchange == "GATEIO":
            return gateio.obtener_ordenes(symbol=symbol)
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES")
        print(e)
        print("")
# -------------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(exchange, symbol, orderId):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            binance_.cancelar_orden(symbol=symbol, orderId=orderId)

        # BYBIT
        if exchange == "BYBIT":
            bybit.cancelar_orden(symbol=symbol, orderId=orderId)

        # BITGET
        if exchange == "BITGET":
            bitget.cancelar_orden(symbol=symbol, orderId=orderId)

        # BINGX
        if exchange == "BINGX":
            bingx.cancelar_orden(symbol=symbol, orderId=orderId)

        # OKX
        if exchange == "OKX":
            okx_.cancelar_orden(symbol=symbol, orderId=orderId)

        # KUCOIN
        if exchange == "KUCOIN":
            kucoin.cancelar_orden(symbol=symbol, orderId=orderId)

        # KUCOIN
        if exchange == "GATEIO":
            gateio.cancelar_orden(symbol=symbol, orderId=orderId)
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {id} DE {exchange}")
        print(e)
        print("")
# -----------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(exchange, symbol):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            return binance_.obtener_posicion(symbol)

        # BYBIT
        if exchange == "BYBIT":
            return bybit.obtener_posicion(symbol)

        # BITGET
        if exchange == "BITGET":
            return bitget.obtener_posicion(symbol)

        # BINGX
        if exchange == "BINGX":
            return bingx.obtener_posicion(symbol)

        # OKX
        if exchange == "OKX":
            return okx_.obtener_posicion(symbol)

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.obtener_posicion(symbol)

        # GATEIO
        if exchange == "GATEIO":
            return gateio.obtener_posicion(symbol)

    except Exception as e:
        print(f"ERROR OBTENIENDO INFO DE LAS POSICIONES DE {exchange}")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(exchange, symbol, positionSide):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # Mensaje
        print(f"Cerrando posición {positionSide} de {symbol} en {exchange}")
        print("")

        # BINANCE
        if exchange == "BINANCE":
            return binance_.cerrar_posicion(symbol, positionSide)

        # BYBIT
        if exchange == "BYBIT":
            return bybit.cerrar_posicion(symbol, positionSide)

        # BITGET
        if exchange == "BITGET":
            return bitget.cerrar_posicion(symbol, positionSide)

        # BINGX
        if exchange == "BINGX":
            return bingx.cerrar_posicion(symbol, positionSide)

        # OKX
        if exchange == "OKX":
            return okx_.cerrar_posicion(symbol, positionSide)

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.cerrar_posicion(symbol)

        # GATEIO
        if exchange == "GATEIO":
            return gateio.cerrar_posicion(symbol, positionSide)

    except Exception as e:
        print(f"ERROR CERRANDO POSICION EN {exchange}")
        print(e)
        print("")
# -------------------------------

#print(precio_actual_activo(exchange="okx", symbol="BTC"))
#nueva_orden(exchange="gateio", symbol="ordi", order_type="market", quantity=0.6, price=43.8, side="sell", leverage=20)
#cancelar_ordenes(exchange="gateio", symbol="ordi")
#print(obtener_ordenes(exchange="gateio", symbol="ordi"))
#cancelar_orden(exchange="gateio", symbol="ordi", orderId=487285852363)
#print(obtener_posicion(exchange="gateio", symbol="ordi"))
#cerrar_posicion("gateio", "ordi", "long")
print("")
