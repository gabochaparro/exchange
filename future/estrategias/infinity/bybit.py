import credenciales
from pybit.unified_trading import HTTP
import json
import time


# Definir la session para Bybit
bybit_session = HTTP(
                    testnet=False,
                    api_key=credenciales.bybit_api_key,
                    api_secret=credenciales.bybit_api_secret,
                )


# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        
        # Precio actual en BYBIT
        precio = float(bybit_session.get_public_trade_history(category="linear",symbol=symbol,limit=1,)['result']['list'][0]['price'])
        return precio
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BYBIT")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Obtener el apalancamiento máximo
        max_leverage = bybit_session.get_instruments_info(category="linear", symbol=symbol)['result']['list'][0]['leverageFilter']['maxLeverage']
        return int(float(max_leverage))
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BYBIT")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE BYBIT NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancamiento_actual = (bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if apalancamiento_actual != str(leverage):
            bybit_session.set_leverage(category="linear", symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))

        # Definir el lado para el modo hedge
        if side == "BUY":
            positionSide = 1
        if side == "SELL":
            positionSide = 2

        # Coloca la orden "LIMIT" o "MARKET"
        if order_type == "LIMIT":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                price=price,
                timeinforce="GTC",
                positionIdx=positionSide
            )
        if order_type == "MARKET":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                positionIdx=positionSide
            )
        print(f"Orden colocada en {price}. ID:", order["result"]["orderId"])
        print("")

        return {
                "orderId": order["result"]["orderId"],
                "price": price
                }
    
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BYBIT")
        print(e)
        print("")
# --------------------------------------------------- 

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:
        
        print("Cancelando ordenes...")
        ordenes_abiertas = bybit_session.get_open_orders(category="linear",symbol=symbol)["result"]['list']
        if len(ordenes_abiertas) > 0:
            bybit_session.cancel_all_orders(category="linear", symbol=symbol)
            print("Se cancelaron todas las ordenes")
            print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BYBIT")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol, orderId=""):
    try:
        return bybit_session.get_open_orders(category="linear",symbol=symbol,orderId=orderId)["result"]['list']

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BYBIT")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:

        if orderId == "":
            print("Eliminando todas las ordenes...")
            bybit_session.cancel_all_orders(category="linear",symbol=symbol)
            print("Todas las ordenes eliminadas.")
            print("")
        else:
            print(f"Eliminando orden {orderId}...")
            bybit_session.cancel_order(category="linear",symbol=symbol,orderId=orderId)
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

        return bybit_session.get_positions(category="linear",symbol=symbol)["result"]["list"]

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
            side = "Sell"
            positionIdx = 1
        if positionSide == "SHORT":
            side = "Buy"
            positionIdx = 2
            
        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(bybit_session.place_order(
                                    category="linear",
                                    symbol= symbol,
                                    side=side,
                                    orderType="Market",
                                    qty="0",
                                    reduceOnly=True,
                                    closeOnTrigger=True,
                                    positionIdx=positionIdx
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
def stop_loss(symbol, positionSide, stopPrice, slSize=""):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            positionSide = 1
        if positionSide == "SHORT":
            positionSide = 2
        
        # Colocar la orden de Stop Loss
        if slSize == "":
            orden = bybit_session.set_trading_stop(
                                        category="linear",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Full",
                                        positionIdx=positionSide
                                    )
        else:
            orden = bybit_session.set_trading_stop(
                                        category="linear",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Partial",
                                        slSize=slSize,
                                        positionIdx=positionSide
                                        )
        
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if orden['orderStatus'] == "Untriggered" and 0.999*stopPrice <= float(orden['triggerPrice']) <= 1.001*stopPrice and orden['reduceOnly'] == True:
        
                print(f"Stop Loss Colocado en {orden['triggerPrice']}.")
                print("")
                
                return {
                "orderId": orden["orderId"],
                "price": orden['triggerPrice']
                }
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN BYBIT")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type, tpSize=""):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            positionSide = 1
            if tpSize == "":
                tpSize = obtener_posicion(symbol=symbol)[0]['size']
        if positionSide == "SHORT":
            positionSide = 2
            if tpSize == "":
                tpSize = obtener_posicion(symbol=symbol)[1]['size']

        if type.upper() == "MARKET":
            type = "Market"
        if type.upper() == "LIMIT":
            type = "Limit"
        
        # Colocar Take Profit
        orden = bybit_session.set_trading_stop(
                                    category="linear",
                                    symbol=symbol,
                                    takeProfit=str(stopPrice),
                                    tpLimitPrice=str(stopPrice),
                                    tpslMode="Partial",
                                    tpSize=tpSize,
                                    tpOrderType=type,
                                    positionIdx=positionSide
                                    )
        
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if orden['orderStatus'] == "Untriggered" and 0.999*stopPrice <= float(orden['triggerPrice']) <= 1.001*stopPrice and orden['reduceOnly'] == True:
                
                print(f"Take Profit Colocado en {stopPrice}.")
                print("")

                return {
                "orderId": orden["orderId"],
                "price": orden['price']
                }
    
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
            positionSide = 1
        if positionSide == "SHORT":
            positionSide = 2
        
        # Colocar la orden de Trailing Stop
        orden = bybit_session.set_trading_stop(
                                    category="linear",
                                    symbol=symbol,
                                    tpslMode="Full",
                                    trailingStop=str(callbackRate*activationPrice/100),
                                    activePrice=str(activationPrice),
                                    positionIdx=positionSide,
                                )
        
        print(f"Trailing Stop Colocado en {activationPrice}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN BYBIT")
        print(e)
        print("")
# -----------------------------------

# FUNCIÓN QUE OBTIENE EL MONTO DISPONIBLE DE LA CUENTA
# ----------------------------------------------------
def patrimonio():
    try:
        return float(bybit_session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalEquity'])
    
    except Exception as e:
        print("ERROR OBTENIENDO EL PATRIMONIO ACTUAL")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE OBTIENE EL MARGEN DISPONIBLE
# ----------------------------------------
def margen_disponible():
    try:
        return float(bybit_session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalAvailableBalance'])
    
    except Exception as e:
        print("ERROR OBTENIENDO EL MARGEN DISPONIBLE")
        print(e)
        print("")
# ----------------------------------------