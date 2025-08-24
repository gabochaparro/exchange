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
        return None
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

# FUNCIÓN QUE CAMBIA EL APALANCAMIENTO DE UN TICK
# ------------------------------------------------------
def apalancamiento(symbol,leverage):
    try:
        
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancamiento_actual = float(bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if round(apalancamiento_actual,2) != round(float(leverage),2):
            bybit_session.set_leverage(category="linear", symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))
    
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
        apalancamiento_actual = float(bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if round(apalancamiento_actual,2) != round(float(leverage),2):
            bybit_session.set_leverage(category="linear", symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))

        # Definir el lado para el modo hedge
        positionSide = 0
        if side == "BUY":
            positionSide = 1
        if side == "SELL":
            positionSide = 2

        # Definir la cantidad exacta que permite el bybit
        cantidad_paso = float(bybit_session.get_instruments_info(category="linear", symbol=symbol)['result']['list'][0]['lotSizeFilter']['qtyStep'])
        quantity = round(round(quantity/cantidad_paso)*cantidad_paso, len(str(cantidad_paso).split(".")[-1]))

        # Coloca la orden "LIMIT"
        if order_type.upper() == "LIMIT":
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
        
        # Coloca la orden "MARKET"
        if order_type.upper() == "MARKET":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                positionIdx=positionSide
            )

        # Coloca la orden "CONDITIONAL"
        if order_type.upper() == "CONDITIONAL":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType="MARKET",
                qty=quantity,
                price=price,
                triggerPrice=price,
                triggerBy="LastPrice",
                timeinforce="GTC",
                positionIdx=positionSide,
                triggerDirection=positionSide
            )

        order = obtener_ordenes(symbol, order["result"]["orderId"])
        #print(json.dumps(order,indent=2))
        
        if order_type.upper() == "CONDITIONAL":
            price = float(order[0]["triggerPrice"])
        else:
            price = float(order[0]["price"])
        
        print(f"Orden {order_type.upper()}-{side} de {order[0]['qty']}{symbol.split('USDT')[0]}  colocada en {price}. ID:", order[0]["orderId"])
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

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES CERRADAS
# ----------------------------------------------------
def obtener_historial_ordenes(symbol, orderId=""):
    try:
        return bybit_session.get_order_history(category="linear",symbol=symbol,orderId=orderId,limit=369)['result']['list']

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

        # Definir la cantidad
        if size =="":
            size = 0
            
        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(bybit_session.place_order(
                                    category="linear",
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
def stop_loss(symbol, positionSide, stopPrice, slSize):
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
                                        slSize=str(slSize),
                                        positionIdx=positionSide
                                        )
        
        createdTime = orden['time']
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if orden['orderStatus'] == "Untriggered" and 0.99*float(createdTime) <= float(orden['createdTime']) <= 1.01*float(createdTime) and orden['reduceOnly'] == True:
        
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
            side = "Sell"
            if tpSize == "":
                posiciones = obtener_posicion(symbol=symbol)
                for posicion in posiciones:
                    if posicion['positionIdx'] == positionSide:
                        tpSize = posicion['size']
        if positionSide == "SHORT":
            positionSide = 2
            side = "Buy"
            if tpSize == "":
                posiciones = obtener_posicion(symbol=symbol)
                for posicion in posiciones:
                    if posicion['positionIdx'] == positionSide:
                        tpSize = posicion['size']

        # Obtener ordenes abiertas
        ordenes_abiertas = obtener_ordenes(symbol=symbol)

        # Calcular la cantidad de TP activos
        nro_tps = 0
        for orden in ordenes_abiertas:
            if orden['stopOrderType'] == "PartialTakeProfit":
                nro_tps = nro_tps + 1
        
        if nro_tps < 20:
            if type.upper() == "MARKET":
                type = "Market"
                # Colocar Take Profit
                orden = bybit_session.set_trading_stop(
                                            category="linear",
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
                                            category="linear",
                                            symbol=symbol,
                                            takeProfit=str(stopPrice),
                                            tpLimitPrice=str(stopPrice),
                                            tpslMode="Partial",
                                            tpSize=str(tpSize),
                                            tpOrderType=type,
                                            positionIdx=positionSide
                                            )
        
        else:
            if type.upper() == "MARKET":
                orden = bybit_session.place_order(
                    category="linear",
                    symbol=symbol,
                    side=side,
                    orderType="MARKET",
                    qty=str(tpSize),
                    price=str(stopPrice),
                    triggerPrice=str(stopPrice),
                    triggerBy="LastPrice",
                    timeinforce="GTC",
                    positionIdx=positionSide,
                    triggerDirection=positionSide,
                    reduceOnly=True
                )

            if type.upper() == "LIMIT":
                orden = bybit_session.place_order(
                    category="linear",
                    symbol=symbol,
                    side=side,
                    orderType="Limit",
                    qty=str(tpSize),
                    price=str(stopPrice),
                    timeinforce="GTC",
                    positionIdx=positionSide,
                    reduceOnly=True
                )

        #print (json.dumps(orden, indent=2))
        createdTime = orden['time']
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if 0.99*float(createdTime) <= float(orden['createdTime']) <= 1.01*float(createdTime) and orden['orderStatus'] == "Untriggered" and orden['reduceOnly'] == True:
                
                print(f"Take Profit Colocado en {orden['price']}.")
                print("")

                return {
                "orderId": orden["orderId"],
                "price": orden['price'],
                "qty": orden['qty']
                }
                
        print(f"Take Profit Colocado en {stopPrice}.")
        print("")

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
        patrimonio = float(bybit_session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalEquity'])

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
def margen_disponible():
    try:
        return float(bybit_session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalAvailableBalance'])
    
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

# FUNCIÓN QUE CAMBIA EL MODO DE POSICIÓN
# --------------------------------------
def cambiar_modo(symbol):
    try:
        bybit_session.switch_position_mode(category="linear", symbol=symbol, mode=3)
    except Exception as e:
        print("ERROR CAMBIANDO EL MODO EN BYBIT")
        print(e)
        print("")
# --------------------------------------

# FUNCIÓN QUE CAMBIA EL TIPO DE MARGEN
# ------------------------------------
def cambiar_margen(symbol,tradeMode):
    try:
        # Definir el tipo de margen
        if tradeMode.upper() == "CROSS" or tradeMode.upper() == "CRUZADO":
            tradeMode = 0
        if tradeMode.upper() == "ISOLATED" or tradeMode.upper() == "AISLADO":
            tradeMode = 1
        
        # Cambiar el tipo de margen
        bybit_session.switch_margin_mode(category='linear', symbol=symbol, tradeMode=tradeMode, buyLeverage="3", sellLeverage="3")
    
    except Exception as e:
        print("ERROR CAMBIANDO EL TIPO DE MARGEN EN BYBIT")
        print(e)
        print("")
# ------------------------------------

# FUNCIÓN QUE OPTIENE EL PASO EN LA CANTIDAD DE UN ACTIVO
# -------------------------------------------------------
def qtyStep(symbol):
    try:
        return float(bybit_session.get_instruments_info(category="linear", symbol=symbol)['result']['list'][0]['lotSizeFilter']['qtyStep'])
    
    except Exception as e:
        print(f"ERROR EN LA FUNCIÓN: qtyStep()\n{e}") 
# -------------------------------------------------------

# FUNCIÓN QUE OBTIENE EL VALOR DE LA COMISIÓN POR OPERACION
# ---------------------------------------------------------
def comision(symbol):
    try:
        return float(bybit_session.get_fee_rates(category="linear", symbol=symbol)['result']['list'][0]['takerFeeRate'])
    except Exception as e:
        print(f"ERROR EN comision()\n{e}")
# ---------------------------------------------------------

#orden = patrimonio()
#orden = margen_disponible()
#orden = nueva_orden("MELANIAUSDT","LIMIT",4,1.428,"SELL",9)
#orden = take_profit("TREEUSDT","SHORT",0.46532,"LIMIT",10.6)
#orden = cambiar_margen("XVGUSDT", "ISOLATED")
#orden = stop_loss("MELANIAUSDT","SHORT",1.45, "")
#orden = obtener_ordenes("ETHUSDT")
#orden = obtener_historial_ordenes("BROCCOLIUSDT")
#orden = qtyStep("OPUSDT")
#orden = obtener_posicion("MYXUSDT")
#print(json.dumps(orden, indent=2))