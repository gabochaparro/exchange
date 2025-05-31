import binance_inverse
import bybit_inverse
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

        return symbol
    
    except Exception as e:
        print("ERROR EN LA DEFICIÓN DEL SÍMBOLO")
# ----------------------------------------------

# FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT
#------------------------------------------------------
def buscar_ticks(exchange):
    try:
        exchange = exchange.upper()
        
        # BINANCE
        if exchange == "BINANCE":
            return binance_inverse.buscar_ticks()
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT (buscar_ticks())")
        print(e)
        print("")
        return []
#-------------------------------------------------------------

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
            precio = binance_inverse.precio_actual_activo(symbol)

        # BYBIT
        if exchange == "BYBIT":
            precio = bybit_inverse.precio_actual_activo(symbol)

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
            orden = binance_inverse.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # BYBIT
        if exchange == "BYBIT":
            orden = bybit_inverse.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # BITGET
        if exchange == "BITGET":
            orden = orden = bitget.nueva_orden(symbol, order_type, quantity, price, side, leverage)    

        # BINGX
        if exchange == "BINGX":
            orden = bingx.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # OKX
        if exchange == "OKX":
            orden = okx_.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # KUCOIN
        if exchange == "KUCOIN":
            orden = kucoin.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # GATEIO
        if exchange == "GATEIO":
            orden = gateio.nueva_orden(symbol, order_type, quantity, price, side, leverage)

        return orden

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
            binance_inverse.cancelar_ordenes(symbol=symbol)
        
        # BYBIT
        if exchange == "BYBIT":
            bybit_inverse.cancelar_ordenes(symbol=symbol)
        
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
def obtener_ordenes(exchange, symbol, orderId=""):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            return binance_inverse.obtener_ordenes(symbol=symbol)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.obtener_ordenes(symbol=symbol,orderId=orderId)

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

# FUNCIÓN QUE BUSCA LA INFO DE TODAS LAS ORDENES CERRADAS
# -------------------------------------------------------
def obtener_historial_ordenes(exchange, symbol, orderId="", limit=369):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            return binance_inverse.obtener_historial_ordenes(symbol=symbol,limit=limit)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.obtener_historial_ordenes(symbol=symbol,orderId=orderId,limit=limit)

        # BITGET
        if exchange == "BITGET":
            return bitget.obtener_historial_ordenes(symbol=symbol)

        # BINGX
        if exchange == "BINGX":
            return bingx.obtener_historial_ordenes(symbol=symbol)

        # OKX
        if exchange == "OKX":
            return okx_.obtener_historial_ordenes(symbol=symbol)

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.obtener_historial_ordenes(symbol=symbol)

        # GATEIO
        if exchange == "GATEIO":
            return gateio.obtener_historial_ordenes(symbol=symbol)
    
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
            binance_inverse.cancelar_orden(symbol=symbol, orderId=orderId)

        # BYBIT
        if exchange == "BYBIT":
            bybit_inverse.cancelar_orden(symbol=symbol, orderId=orderId)

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
            return binance_inverse.obtener_posicion(symbol)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.obtener_posicion(symbol)

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
def cerrar_posicion(exchange, symbol, positionSide, size=""):
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
            return binance_inverse.cerrar_posicion(symbol, positionSide)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.cerrar_posicion(symbol, positionSide, size=size)

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

# FUNCIÓM QUE COLOCA UN STOP LOSS
# -------------------------------
def stop_loss(exchange, symbol, positionSide, stopPrice, slSize=""):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()
        positionSide = positionSide.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # Mensaje
        print(f"Colocando Stop Loss al {positionSide} de {symbol} en {exchange}")
        print("")

        # BINANCE
        if exchange == "BINANCE":
            binance_inverse.stop_loss(symbol, positionSide, stopPrice)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.stop_loss(symbol, positionSide, stopPrice, slSize=slSize)

        # BITGET
        if exchange == "BITGET":
            bitget.stop_loss(symbol, positionSide, stopPrice)

        # BINGX
        if exchange == "BINGX":
            bingx.stop_loss(symbol, positionSide, stopPrice)

        # OKX (NO FUNCIONA AUN)
        if exchange == "OKX":
            okx_.stop_loss(symbol, positionSide, stopPrice)

        # KUCOIN
        if exchange == "KUCOIN":
            kucoin.stop_loss(symbol, positionSide, stopPrice)

        # GATEIO
        if exchange == "GATEIO":
            gateio.stop_loss(symbol, positionSide, stopPrice)
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS")
        print(e)
        print("")
# -------------------------------

# FUNCIÓM QUE COLOCA UN TAKE PROFIT
# ---------------------------------
def take_profit(exchange, symbol, positionSide, stopPrice, type, tpSize=""):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()
        positionSide = positionSide.upper()
        type = type.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # Mensaje
        print(f"Colocando Take Profit al {positionSide} de {symbol} en {exchange}")
        print("")

        # BINANCE
        if exchange == "BINANCE":
            return binance_inverse.take_profit(symbol, positionSide, stopPrice, type, tpSize=tpSize)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.take_profit(symbol, positionSide, stopPrice, type, tpSize=tpSize)

        # BITGET (SOLO MARKET POR EL MOMENTO)
        if exchange == "BITGET":
            return bitget.take_profit(symbol, positionSide, stopPrice, type)

        # BINGX
        if exchange == "BINGX":
            return bingx.take_profit(symbol, positionSide, stopPrice, type)

        # OKX (SOLO LIMIT POR EL MOMENTO)
        if exchange == "OKX":
            return okx_.take_profit(symbol, positionSide, stopPrice, type)

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.take_profit(symbol, positionSide, stopPrice, type)

        # GATEIO
        if exchange == "GATEIO":
            return gateio.take_profit(symbol, positionSide, stopPrice, type)
    
    except Exception as e:
        print("ERROR COLOCANDO TAKE PROFIT")
        print(e)
        print("")
# ---------------------------------

# FUNCIÓM QUE COLOCA UN TRAINLING STOP
# -------------------------------
def trailing_stop(exchange, symbol, positionSide, activationPrice, callbackRate):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()
        positionSide = positionSide.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # Mensaje
        print(f"Colocando Trailing Stop al {positionSide} de {symbol} en {exchange}")
        print("")

        # BINANCE
        if exchange == "BINANCE":
            return binance_inverse.trailing_stop(symbol, positionSide, activationPrice, callbackRate)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.trailing_stop(symbol, positionSide, activationPrice, callbackRate)

        # BITGET
        if exchange == "BITGET":
            return bitget.trailing_stop(symbol, positionSide, activationPrice, callbackRate)

        # BINGX
        if exchange == "BINGX":
            return bingx.trailing_stop(symbol, positionSide, activationPrice, callbackRate)

        # OKX
        if exchange == "OKX":
            return okx_.trailing_stop(symbol, positionSide, activationPrice, callbackRate)

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.trailing_stop(symbol, positionSide, activationPrice, callbackRate)

        # GATEIO
        if exchange == "GATIO":
            return gateio.trailing_stop(symbol, positionSide, activationPrice, callbackRate)
    
    except Exception as e:
        print("ERROR COLOCANDO TRAILING STOP")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE OBTIENE EL APALANCAMIENTO MÁXIMO DE UN TICK
# -------------------------------------------------------
def apalancamiento_max(exchange, symbol):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            return binance_inverse.apalancameinto_max(symbol=symbol)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.apalancameinto_max(symbol=symbol)

        # BITGET
        if exchange == "BITGET":
            return bitget.apalancameinto_max(symbol=symbol)

        # BINGX
        if exchange == "BINGX":
            return bingx.apalancameinto_max(symbol=symbol)

        # OKX
        if exchange == "OKX":
            return okx_.apalancameinto_max(symbol=symbol)

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.apalancameinto_max(symbol=symbol)

        # GATEIO
        if exchange == "GATIO":
            return gateio.apalancameinto_max(symbol=symbol)
    
    except Exception as e:
        print("ERROR COLOCANDO TRAILING STOP")
        print(e)
        print("")
# -------------------------------------------------------

# FUNCIÓN QUE CAMBIA EL APALANCAMIENTO DE UN TICK
# ------------------------------------------------------
def apalancamiento(exchange, symbol, leverage):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            binance_inverse.apalancameinto(symbol=symbol,leverage=leverage)

        # BYBIT
        if exchange == "BYBIT":
            bybit_inverse.apalancameinto(symbol=symbol,leverage=leverage)

        # BITGET
        if exchange == "BITGET":
            bitget.apalancameinto(symbol=symbol,leverage=leverage)

        # BINGX
        if exchange == "BINGX":
            bingx.apalancameinto(symbol=symbol,leverage=leverage)

        # OKX
        if exchange == "OKX":
            okx_.apalancameinto(symbol=symbol,leverage=leverage)

        # KUCOIN
        if exchange == "KUCOIN":
            kucoin.apalancameinto(symbol=symbol,leverage=leverage)

        # GATEIO
        if exchange == "GATIO":
            gateio.apalancameinto(symbol=symbol,leverage=leverage)
    
    except Exception as e:
        print(f"ERROR CAMBIANDO EL APALANCAMIENTO DE {symbol}")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN QUE OBTIENE EL PATRIMONIO DE LA CUENTA
# ----------------------------------------------------
def patrimonio(exchange, symbol):
    try:

        exchange = exchange.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            return binance_inverse.patrimonio(symbol)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.patrimonio(symbol)

        # BITGET
        if exchange == "BITGET":
            return bitget.patrimonio()

        # BINGX
        if exchange == "BINGX":
            return bingx.patrimonio()

        # OKX
        if exchange == "OKX":
            return okx_.patrimonio()

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.patrimonio()

        # GATEIO
        if exchange == "GATIO":
            return gateio.patrimonio()
    
    except Exception as e:
        print("ERROR OBTENIENDO EL PATRIMONIO DE LA CUENTA")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE OBTIENE EL MARGEN DISPONIBLE
# ----------------------------------------
def margen_disponible(exchange, symbol):
    try:

        exchange = exchange.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            return binance_inverse.margen_disponible(symbol)

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.margen_disponible(symbol)

        # BITGET
        if exchange == "BITGET":
            return bitget.margen_disponible()

        # BINGX
        if exchange == "BINGX":
            return bingx.margen_disponible()

        # OKX
        if exchange == "OKX":
            return okx_.margen_disponible()

        # KUCOIN
        if exchange == "KUCOIN":
            return kucoin.margen_disponible()

        # GATEIO
        if exchange == "GATIO":
            return gateio.margen_disponible()
    
    except Exception as e:
        print("ERROR OBTENIENDO EL MARGEN DISPONIBLE")
        print(e)
        print("")
# ----------------------------------------
# 
# # FUNCIÓN QUE CAMBIA EL MODO DE POSICIÓN
# --------------------------------------
def cambiar_modo(exchange, symbol):
    try:

        exchange = exchange.upper()
        
        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            pass

        # BYBIT
        if exchange == "BYBIT":
            pass

        # BITGET
        if exchange == "BITGET":
            pass

        # BINGX
        if exchange == "BINGX":
            pass

        # OKX
        if exchange == "OKX":
            pass

        # KUCOIN
        if exchange == "KUCOIN":
            pass

        # GATEIO
        if exchange == "GATIO":
            pass
    
    except Exception as e:
        print("ERROR CAMBIANDO EL MODO")
        print(e)
        print("")
# --------------------------------------
# 
# # FUNCIÓN QUE CAMBIA EL TIPO DE MARGEN
# --------------------------------------
def cambiar_margen(exchange, symbol, margin_mode):
    try:

        exchange = exchange.upper()
        
        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)

        # BINANCE
        if exchange == "BINANCE":
            pass

        # BYBIT
        if exchange == "BYBIT":
            return bybit_inverse.cambiar_margen(symbol, margin_mode)

        # BITGET
        if exchange == "BITGET":
            pass

        # BINGX
        if exchange == "BINGX":
            pass

        # OKX
        if exchange == "OKX":
            pass

        # KUCOIN
        if exchange == "KUCOIN":
            pass

        # GATEIO
        if exchange == "GATIO":
            pass
    
    except Exception as e:
        print("ERROR CAMBIANDO EL TIPO DE MARGEN")
        print(e)
        print("")
# --------------------------------------

#orden = buscar_ticks("binance")
#orden = precio_actual_activo(exchange="bybit", symbol="BTC")
#orden = nueva_orden(exchange="bybit", symbol="btc", order_type="limit", quantity=3, price=65080.0, side="buy", leverage=3.6)
#orden = cancelar_ordenes(exchange="bybit", symbol="btc")
#orden = obtener_ordenes(exchange="bybit", symbol="btc")
#orden = obtener_historial_ordenes("bybit","BTC")
#orden = cancelar_orden(exchange="bybit", symbol="btc", orderId="864b343f-33a7-4b1e-8659-d895ea998066")
#orden = obtener_posicion(exchange="bybit", symbol="btc")
#cerrar_posicion("gateio", "rats", "long")
#orden = stop_loss(exchange="bybit", symbol="btc", positionSide="short", stopPrice=66700)
#orden = take_profit("binance", "eth", "short", 2840, "limit", 1)
#orden = trailing_stop(exchange="bybit", symbol="btc", positionSide="short", activationPrice=65000, callbackRate=1)
#orden = apalancamiento_max("binance","eth")
#print(json.dumps(orden,indent=2))
