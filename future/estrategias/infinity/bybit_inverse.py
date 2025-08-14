from pybit.unified_trading import HTTP
import json
import time


# Obtener credenciales
credenciales = json.load(open("future/estrategias/infinity/credenciales.json","r"))

# Definir la session para Bybit
bybit_session = HTTP(
                    testnet=False,
                    api_key=credenciales['api_key'],
                    api_secret=credenciales['api_secret'],
                )
category = "inverse"


# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        
        # Precio actual en BYBIT
        precio = float(bybit_session.get_public_trade_history(category=category,symbol=symbol.upper(),limit=1,)['result']['list'][0]['price'])
        return precio
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BYBIT")
        print(e)
        print("")
        return None
#--------------------------------------------------------

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Obtener el apalancamiento máximo
        max_leverage = bybit_session.get_instruments_info(category=category, symbol=symbol.upper())['result']['list'][0]['leverageFilter']['maxLeverage']
        return int(float(max_leverage))
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BYBIT")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN QUE CAMBIA EL APALANCAMIENTO DE UN TICK
# ------------------------------------------------------
def apalancameinto(symbol,leverage):
    try:
        
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancamiento_actual = float(bybit_session.get_positions(category="inverse", symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if round(apalancamiento_actual,2) != round(float(leverage),2):
            bybit_session.set_leverage(category="inverse", symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))
    
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
        apalancamiento_actual = float(bybit_session.get_positions(category=category, symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if round(apalancamiento_actual,2) != round(float(leverage),2):
            bybit_session.set_leverage(category=category, symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))

        # Definir el lado para el modo hedge
        if symbol.split(symbol.split("USD")[0])[-1] == "USD":
            positionSide = 0
            if side =="BUY":
                triggerDirection = 1
            if side == "SELL":
                triggerDirection = 2
        else:
            if side == "BUY":
                positionSide = 1
                triggerDirection = 1
            if side == "SELL":
                positionSide = 2
                triggerDirection = 2

        # Definir la cantidad exacta que permite bybit
        cantidad_paso = float(bybit_session.get_instruments_info(category=category, symbol=symbol)['result']['list'][0]['lotSizeFilter']['qtyStep'])
        quantity = round(quantity/cantidad_paso)*cantidad_paso

        # Coloca la orden "LIMIT"
        if order_type.upper() == "LIMIT":
            order = bybit_session.place_order(
                category=category,
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                price=price,
                timeinforce="GTC",
                positionIdx=positionSide
            )
        
        # Coloca la orden "MARKET"
        if order_type.upper() == "MARKET":
            order = bybit_session.place_order(
                category=category,
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                positionIdx=positionSide
            )

        # Coloca la orden "CONDITIONAL"
        if order_type.upper() == "CONDITIONAL":
            order = bybit_session.place_order(
                category=category,
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType="MARKET",
                qty=quantity,
                price=price,
                triggerPrice=price,
                triggerBy="LastPrice",
                timeinforce="GTC",
                positionIdx=positionSide,
                triggerDirection=triggerDirection
            )

        order = obtener_ordenes(symbol, order["result"]["orderId"])
        #print(json.dumps(order,indent=2))
        
        if order_type.upper() == "CONDITIONAL":
            price = float(order[0]["triggerPrice"])
        else:
            price = float(order[0]["price"])
        
        print(f"Orden {order_type.upper()}-{side} de {order[0]['qty']} {symbol.split('USDT')[0]}  colocada en {price}. ID:", order[0]['orderId'])
        print("")

        
        return {
                "orderId": order[0]["orderId"],
                "price": price,
                "qty": float(order[0]["qty"])
                }
    
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BYBIT")
        print(e)
        print("")
# ---------------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol, orderId=""):
    try:
        return bybit_session.get_open_orders(category="inverse",symbol=symbol.upper(),orderId=orderId)["result"]['list']

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
        ordenes_abiertas = bybit_session.get_open_orders(category="inverse",symbol=symbol)["result"]['list']
        if len(ordenes_abiertas) > 0:
            bybit_session.cancel_all_orders(category="inverse", symbol=symbol)
            print("Se cancelaron todas las ordenes")
            print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BYBIT")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES CERRADAS
# ----------------------------------------------------
def obtener_historial_ordenes(symbol, orderId="", limit=369):
    try:
        return bybit_session.get_order_history(category="inverse",symbol=symbol.upper(),orderId=orderId,limit=limit)['result']['list']

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
            bybit_session.cancel_all_orders(category="inverse",symbol=symbol)
            print("Todas las ordenes eliminadas.")
            print("")
        else:
            print(f"Eliminando orden {orderId}...")
            bybit_session.cancel_order(category="inverse",symbol=symbol,orderId=orderId)
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

        return bybit_session.get_positions(category="inverse",symbol=symbol.upper())["result"]["list"]

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BYBIT")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(symbol, positionSide, size=""):
    try:
        
        # Definir el lado segun la posición
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "Sell"
            positionIdx = 1
        if positionSide == "SHORT":
            side = "Buy"
            positionIdx = 2
        if symbol.split(symbol.split("USD")[0])[-1] == "USD":
            positionIdx = 0

        # Definir la cantidad
        if size =="":
            size = 0
            
        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(bybit_session.place_order(
                                    category="inverse",
                                    symbol= symbol,
                                    side=side,
                                    orderType="Market",
                                    qty=str(size),
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
        if symbol.split(symbol.split("USD")[0])[-1] == "USD":
            positionSide = 0
        
        # Colocar la orden de Stop Loss
        if slSize == "":
            orden = bybit_session.set_trading_stop(
                                        category="inverse",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Full",
                                        positionIdx=positionSide
                                    )
        else:
            orden = bybit_session.set_trading_stop(
                                        category="inverse",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Partial",
                                        slSize=str(slSize),
                                        positionIdx=positionSide
                                        )
        
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if orden['orderStatus'] == "Untriggered" and 0.999*float(stopPrice) <= float(orden['triggerPrice']) <= 1.001*float(stopPrice) and orden['reduceOnly'] == True:
        
                print(f"Stop Loss Colocado en {orden['triggerPrice']}.")
                print("")
                
                return {
                "orderId": orden["orderId"],
                "price": orden['triggerPrice'],
                "qty": orden['qty']
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
                posiciones = obtener_posicion(symbol=symbol)
                for posicion in posiciones:
                    if posicion['positionIdx'] == positionSide:
                        tpSize = posicion['size']
        if positionSide == "SHORT":
            positionSide = 2
            if tpSize == "":
                posiciones = obtener_posicion(symbol=symbol)
                for posicion in posiciones:
                    if posicion['positionIdx'] == positionSide:
                        tpSize = posicion['size']
        if symbol.split(symbol.split("USD")[0])[-1] == "USD":
            positionSide = 0
            if tpSize == "":
                for posicion in posiciones:
                    if posicion['positionIdx'] == positionSide:
                        tpSize = posicion['size']

        if type.upper() == "MARKET":
            type = "Market"
            # Colocar Take Profit
            orden = bybit_session.set_trading_stop(
                                        category=category,
                                        symbol=symbol,
                                        tpslMode="Partial",
                                        tpSize=str(tpSize),
                                        tpOrderType=type,
                                        positionIdx=positionSide
                                        )
        
        if type.upper() == "LIMIT":
            type = "Limit"
            # Colocar Take Profit
            orden = bybit_session.set_trading_stop(
                                        category=category,
                                        symbol=symbol,
                                        takeProfit=str(stopPrice),
                                        tpLimitPrice=str(stopPrice),
                                        tpslMode="Partial",
                                        tpSize=str(tpSize),
                                        tpOrderType=type,
                                        positionIdx=positionSide
                                        )
        
        
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if orden['orderStatus'] == "Untriggered" and 0.99*float(stopPrice) <= float(orden['triggerPrice']) <= 1.01*float(stopPrice) and orden['reduceOnly'] == True:
                
                print(f"Take Profit Colocado en {orden['price']}.")
                print("")

                return {
                "orderId": orden["orderId"],
                "price": orden['triggerPrice'],
                "qty": orden['qty']
                }

        return {
            "orderId": "-",
            "price": str(stopPrice),
            "qty": str(tpSize)
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
        if symbol.split(symbol.split("USD")[0])[-1] == "USD":
            positionSide = 0
        
        # Colocar la orden de Trailing Stop
        orden = bybit_session.set_trading_stop(
                                    category="inverse",
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
def patrimonio(symbol):
    try:
        symbol = symbol.upper().split("USD")[0].upper()
        patrimonio = float(bybit_session.get_wallet_balance(accountType="UNIFIED", coin=symbol)['result']['list'][0]['coin'][0]['equity'])
    
        if patrimonio != None:
            return patrimonio
        else:
            print("ERROR OBTENIENDO EL PATRIMONIO ACTUAL")
            print(patrimonio)
            print("")

    except Exception as e:
        print("ERROR OBTENIENDO EL PATRIMONIO ACTUAL")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE OBTIENE EL MARGEN DISPONIBLE
# ----------------------------------------
def margen_disponible(symbol):
    try:
        
        symbol = symbol.upper().split("USD")[0].upper()
        return float(bybit_session.get_wallet_balance(accountType="UNIFIED", coin=symbol)['result']['list'][0]['coin'][0]['equity'])
    
    except Exception as e:
        print("ERROR OBTENIENDO EL MARGEN DISPONIBLE")
        print(e)
        print("")
# ----------------------------------------

# FUNCIÓN QUE OBTIENE EL BALANCE TOTAL DE LA CUENTA
# -------------------------------------------------
def balance_total():
    try:
        return float(bybit_session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalWalletBalance'])
    
    except Exception as e:
        print("ERROR OBTENIENDO EL BALANCE TOTAL")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CAMBIA EL TIPO DE MARGEN
# ------------------------------------
def cambiar_margen(symbol,tradeMode):
    try:
        # Definir el tipo de margen
        if tradeMode.upper() == "CROSS" or tradeMode.upper() == "CRUZADO":
            tradeMode = 0
            if tradeMode == "ISOLATED" or tradeMode.upper() == "AISLADO":
                tradeMode = 1
        
        # Cambiar el tipo de margen
        bybit_session.switch_margin_mode(category='inverse', symbol=symbol, tradeMode=tradeMode, buyLeverage="3", sellLeverage="3")
    
    except Exception as e:
        print("ERROR CAMBIANDO EL TIPO DE MARGEN EN BYBIT")
        print(e)
        print("")
# ------------------------------------


#orden = precio_actual_activo("btcusd")
#orden = apalancameinto_max("ethusd")
#orden = obtener_ordenes("solusd")
#orden = cancelar_ordenes("BTCUSD")
#orden = obtener_historial_ordenes("solUSD")
#orden = nueva_orden(symbol="BTCUSD", order_type="Conditional", quantity=1, price=99999, side="BUY", leverage=3)
#orden = cancelar_orden("BTCUSD", orderId="b0cdc9fa-40b9-461b-9dff-e5897d9caac0")
#orden = obtener_posicion("BTCUSD")
#orden = cerrar_posicion("BTCUSD", "LONG")
#orden = stop_loss("BTCUSD", "SHORT", 66700)
#orden = take_profit("BTCUSD", "SHORT", 65223.00, "LIMIT",2)
#orden = trailing_stop("BTCUSD", "SHORT", 65223.00, 0.36)
#orden = patrimonio('ethusd')
#orden = margen_disponible("ethusd")
#print(json.dumps(orden,indent=2))
