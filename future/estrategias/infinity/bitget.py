import credenciales
import pybitget
import json
import time


# Definir el cliente para BitGet
bitget_client = pybitget.Client(
                            api_key=credenciales.bitget_api_key, 
                            api_secret_key=credenciales.bitget_api_secret, 
                            passphrase = credenciales.bitget_api_passphrase, 
                            use_server_time=False,
                        )

# Parametros Generales
marginCoin = "USDT"
productType = "umcbl"

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        precio = bitget_client.mix_get_single_symbol_ticker(symbol=symbol)['data']['last']
        return float(precio)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BITGET")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Obtener el apalancamiento máximo
        max_leverage = bitget_client.mix_get_leverage(symbol=symbol)['data']['maxLeverage']
        return int(float(max_leverage))
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BITGET")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE BITGET NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:

        # Modificar apalancamiento
        max_leverage = apalancameinto_max(symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        bitget_client.mix_adjust_leverage(symbol=symbol, marginCoin=marginCoin, leverage=leverage, holdSide=None)

        # Definir el lado
        if side == "BUY":
            side = "OPEN_LONG"
        if side == "SELL":
            side = "OPEN_SHORT"

        # Colocar la orden
        order = bitget_client.mix_place_order(
                                        symbol=symbol, 
                                        marginCoin=marginCoin, 
                                        size=quantity,
                                        side=side, 
                                        orderType=order_type, 
                                        price=price
                                    )
        
        print(f"Orden colocada en {price}. ID:", order["data"]["orderId"])
        print("")

        return {
            "orderId": order["data"]["orderId"],
            "price": price
            }

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BITGET")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        print("Buscando ordenes...")
        ordenes_abiertas = bitget_client.mix_get_open_order(symbol=symbol)['data']
        print(f"{len(ordenes_abiertas)} ordenes encontradas")
        return ordenes_abiertas

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BYBIT")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:

        print("Cancelando ordenes...")
        ordenes_abiertas = obtener_ordenes(symbol)
        for orden in ordenes_abiertas:
            bitget_client.mix_cancel_order(symbol=symbol, marginCoin=marginCoin, orderId=orden['orderId'])
        
        print("Se cancelaron todas las ordenes")
        print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BYBIT")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:
        
        print(f"Eliminando orden {orderId}...")
        bitget_client.mix_cancel_order(symbol=symbol,marginCoin=marginCoin,orderId=str(orderId))
        print(f"Eliminada la orden {orderId} de {symbol}.")
        print("")
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {id} DE BYBIT")
        print(e)
        print("")
# -----------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        return bitget_client.mix_get_single_position(symbol=symbol,marginCoin=marginCoin)['data']

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BYBIT")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(symbol, positionSide):
    try:
        
        # Definir el lado segun la posición
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "close_long"
        if positionSide == "SHORT":
            side = "close_short"
            
        # Obtener cantidad
        cantidad = obtener_posicion(symbol)[0]['available']

        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(bitget_client.mix_place_order(
                                        symbol=symbol, 
                                        marginCoin=marginCoin, 
                                        size=cantidad,
                                        side=side, 
                                        orderType="MARKET", 
                                        price=0
                            ),indent=2))
        
        print(f"Posición {positionSide} Cerrada")
        print("")

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BYBIT")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN STOP LOSS
# -------------------------------
def stop_loss(symbol, positionSide, stopPrice):
    try:

        # Definir parametros
        holdSide = positionSide.lower()
        
        # Colocar la orden de Stop Loss
        orden = orden = bitget_client.mix_place_stop_order(
                                                        symbol=symbol,
                                                        marginCoin=marginCoin,
                                                        planType="loss_plan",
                                                        triggerPrice=str(stopPrice),
                                                        holdSide=holdSide
                                                    )
        
        print(f"Stop Loss Colocado en {stopPrice}. ID: {orden['data']['orderId']}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN BITGET")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type):
    try:

        # Definir parametros
        holdSide = positionSide.lower()

        # Colocar Take Profit (Por ahora la API solo permite a market)
        orden = orden = bitget_client.mix_place_stop_order(
                                                        symbol=symbol,
                                                        marginCoin=marginCoin,
                                                        planType="profit_plan",
                                                        triggerPrice=str(stopPrice),
                                                        holdSide=holdSide
                                                    )
        
        print(f"Take Profit Colocado en {stopPrice}. ID: {orden['data']['orderId']}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO TAKE PROFIT EN BYBIT")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN QUE COLOCA UN TRAILING STOP
# -----------------------------------
def trailing_stop(symbol, positionSide, activationPrice, callbackRate):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "close_long"
        if positionSide == "SHORT":
            side = "close_short"
        
        # callbackRate no puede ser menor que 1%
        if callbackRate < 1:
            callbackRate = 1
        
        # Determinar la cantidad
        posiciones = obtener_posicion(symbol=symbol)
        for posicion in posiciones:
            if posicion['holdSide'] == positionSide.lower():
                size = posicion['available']

        # Colocar la orden de Trailing Stop
        orden = bitget_client.mix_place_trailing_stop_order(
                                                            symbol=symbol,
                                                            marginCoin=marginCoin,
                                                            triggerPrice=str(activationPrice),
                                                            side=side,
                                                            size=size,
                                                            rangeRate=str(callbackRate)
                                                            )
        
        print(f"Trailing Stop Colocado en {activationPrice}. ID: {orden['data']['orderId']}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN BYBIT")
        print(e)
        print("")
# -----------------------------------