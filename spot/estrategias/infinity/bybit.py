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
        return float(bybit_session.get_public_trade_history(category="spot",symbol=symbol,limit=1,)['result']['list'][0]['price'])
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BYBIT")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE BYBIT NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side):
    try:

        # Coloca la orden "LIMIT" o "MARKET"
        if order_type == "LIMIT":
            order = bybit_session.place_order(
                category="spot",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                price=price,
                timeinforce="GTC"
            )
        if order_type == "MARKET":
            order = bybit_session.place_order(
                category="spot",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity
            )
        order = obtener_ordenes(symbol=symbol, orderId=order["result"]["orderId"])[0]
        print(f"Orden colocada en {order['price']}. ID:", order["orderId"])
        print("")

        return {
                "orderId": order["orderId"],
                "price": order['price']
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
        ordenes_abiertas = bybit_session.get_open_orders(category="spot",symbol=symbol)["result"]['list']
        if len(ordenes_abiertas) > 0:
            bybit_session.cancel_all_orders(category="spot", symbol=symbol)
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
        return bybit_session.get_open_orders(category="spot",symbol=symbol,orderId=orderId)["result"]['list']

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BYBIT")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES CERRADAS
# ----------------------------------------------------
def obtener_historial_ordenes(symbol, limit=30, orderId=""):
    try:
        return bybit_session.get_order_history(category="spot",symbol=symbol,limit=limit,orderId=orderId)['result']['list']

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
            bybit_session.cancel_all_orders(category="spot",symbol=symbol)
            print("Todas las ordenes eliminadas.")
            print("")
        else:
            print(f"Eliminando orden {orderId}...")
            bybit_session.cancel_order(category="spot",symbol=symbol,orderId=orderId)
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
        symbol = symbol.split("USDT")[0]

        return (bybit_session.get_wallet_balance(accountType="UNIFIED", coin=symbol)['result']['list'][0]['coin'][0]['walletBalance'])

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BYBIT")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE COLOCA UN STOP LOSS
# -------------------------------
def stop_loss(symbol, stopPrice, slSize=""):
    try:
        
        # Colocar la orden de Stop Loss
        if slSize == "":
            orden = bybit_session.set_trading_stop(
                                        category="spot",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Full"
                                    )
        else:
            orden = bybit_session.set_trading_stop(
                                        category="spot",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Partial",
                                        slSize=slSize
                                        )
        
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if orden['orderStatus'] == "Untriggered" and orden['triggerPrice'] == str(stopPrice) and orden['reduceOnly'] == True:
        
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
def take_profit(symbol, stopPrice, type, tpSize=""):
    try:

        if type.upper() == "MARKET":
            type = "Market"
        if type.upper() == "LIMIT":
            type = "Limit"
            
            # Colocar Take Profit
            orden = bybit_session.set_trading_stop(
                                        category="spot",
                                        symbol=symbol,
                                        takeProfit=str(stopPrice),
                                        tpLimitPrice=str(stopPrice),
                                        tpslMode="Partial",
                                        tpSize=tpSize,
                                        tpOrderType=type
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
        margen = float(bybit_session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalAvailableBalance'])
        if margen != None:
            return margen
    
    except Exception as e:
        print("ERROR OBTENIENDO EL MARGEN DISPONIBLE")
        print(e)
        print("")
# ----------------------------------------