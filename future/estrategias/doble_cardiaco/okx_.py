import credenciales
from okx import Trade, Account, PublicData, MarketData
import json
import time

# Definir la API de OKX
tradeAPI = Trade.TradeAPI(credenciales.okx_api_key, 
                              credenciales.okx_api_secret, 
                              credenciales.okx_api_passphrase, 
                              False, 
                              "0"
                              )
accountAPI = Account.AccountAPI(credenciales.okx_api_key, 
                              credenciales.okx_api_secret, 
                              credenciales.okx_api_passphrase, 
                              False, 
                              "0"
                              )
instType = "SWAP"
tdMode = "cross"

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        precio = MarketData.MarketAPI(flag="0").get_ticker(instId=symbol)['data'][0]['last']
        return float(precio)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN OKX")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Obtener el apalancamiento máximo
        tickes = PublicData.PublicAPI(flag="0").get_instruments(instType=instType)['data']
        for tick in tickes:
            if tick['instId'] == symbol:
                max_leverage = float(tick['lever'])
        return int(max_leverage)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN OKX")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE OKX NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Definir la cantidad segun el tamaño del lote
        tickes = PublicData.PublicAPI(flag="0").get_instruments(instType=instType)['data']
        for tick in tickes:
            if tick['instId'] == symbol:
                lote = float(tick['ctVal'])
                quantity = quantity/lote

        # Definir la posicion segun el lado
        if side == "BUY":
            posSide = "long"
        if side == "SELL":
            posSide = "short"
        
        # Ajustar el apalancamiento
        max_leverage = apalancameinto_max(symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        
        print("")
        accountAPI.set_leverage(
                                    instId=symbol,
                                    lever=str(leverage),
                                    mgnMode=tdMode
                                )
        print("")

        # Colocar la orden
        order = tradeAPI.place_order(
                                        instId=symbol,
                                        tdMode=tdMode,
                                        side=side.lower(),
                                        posSide=posSide,
                                        ordType=order_type.lower(),
                                        px=str(price),
                                        sz=str(quantity)
                                    )
        print("")
        
        if order["code"] == "0":
            print(f"Orden colocada en {price}. ID:", order["data"][0]["ordId"])
            print("")
        else:
            print("ERROR COLOCANDO LA ORDEN EN OKX, error_code = ",order["data"][0]["sCode"], ", Error_message = ", order["data"][0]["sMsg"])
            print("")

        return {
                "orderId": order["data"][0]["ordId"],
                "price": price
                }

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN OKX")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        print("Buscando ordenes...")
        oredenes_abiertas = tradeAPI.get_order_list(instId=symbol, instType=instType,)['data']
        print(f"{len(oredenes_abiertas)} ordenes encontradas")
        return oredenes_abiertas

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN OKX")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:
        
        print(f"Eliminando orden {orderId}...")
        tradeAPI.cancel_order(instId=symbol, ordId=str(orderId),)
        print(f"Eliminada la orden {orderId} de {symbol}.")
        print("")
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {id} DE OKX")
        print(e)
        print("")
# -----------------------------

# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:
        
        print("Cancelando ordenes...")
        ordenes_abiertas = obtener_ordenes(symbol)
        if len(ordenes_abiertas) > 0:
            for orden in ordenes_abiertas:
                ordId = orden['ordId']
                cancelar_orden(symbol, ordId)
            print("Se cancelaron todas las ordenes")
            print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE OKX")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        return accountAPI.get_positions(instType=instType, instId=symbol)['data']

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
        positionSide = positionSide.lower()
            
        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(tradeAPI.close_positions(
                                                    instId=symbol,
                                                    mgnMode=tdMode,
                                                    posSide=positionSide,
                                                  ),indent=2))
        
        print(f"Posición {positionSide} Cerrada")
        print("")

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BYBIT")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN STOP LOSS (Aun No Funciona Bien, Cierra la orden de inmediato)
# -------------------------------
def stop_loss(symbol, positionSide, stopPrice):
    try:

        # Definir parametros
        positionSide = positionSide.lower()
        if positionSide == "long":
            side = "sell"
        if positionSide == "short":
            side = "buy"
        
        # determinar la cantidad
        posiciones = obtener_posicion(symbol=symbol)
        for posicion in posiciones:
            if posicion['posSide'] == positionSide:
                sz = posicion['pos']
        
        # Colocar la orden de Stop Loss
        orden = tradeAPI.place_order(
                                    instId=symbol,
                                    tdMode=tdMode,
                                    side=side,
                                    posSide=positionSide,
                                    ordType="market",
                                    sz= sz,
                                    attachAlgoOrds={
                                                    "slTriggerPx": stopPrice,
                                                    "slOrdPx": stopPrice
                                                    }
                                    )
        print("")
        print(f"Mensaje API: {orden['data'][0]['sMsg']}. ordId: {orden['data'][0]['ordId']}")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN OKX")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET (Solo funciona a limit)
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type):
    try:

        # Definir parametros
        type = type.lower()
        positionSide = positionSide.lower()
        if positionSide == "long":
            side = "sell"
        if positionSide == "short":
            side = "buy"
        
        # determinar la cantidad
        posiciones = obtener_posicion(symbol=symbol)
        for posicion in posiciones:
            if posicion['posSide'] == positionSide:
                sz = posicion['pos']
        
        # Colocar la orden de Stop Loss
        orden = tradeAPI.place_order(
                                        instId=symbol,
                                        tdMode=tdMode,
                                        side=side,
                                        posSide=positionSide,
                                        ordType=type,
                                        sz=sz,
                                        tpTriggerPx=stopPrice,
                                        tpOrdPx=stopPrice,
                                        px=stopPrice
                                    )
        print("")
        print(f"Mensaje API: {orden['data'][0]['sMsg']}. ordId: {orden['data'][0]['ordId']}")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO TAKE PROFIT EN BYBIT")
        print(e)
        print("")
# ------------------------------------------------