from binance.cm_futures import CMFutures
import json
import time


# Obtener credenciales
credenciales = json.load(open("future/estrategias/classic_grid/credenciales.json","r"))

binance_client = CMFutures(
                            key=credenciales['api_key'],
                            secret=credenciales['api_secret']
                            )


# FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT
#------------------------------------------------------
def buscar_ticks():
    try:
        i = 0
        ticks =[]
        lista_ticks = binance_client.ticker_price() #Buscar todos los pares de monedas
        #print ("Cantidad de Monedas encontradas en todos los pares:", len(lista_ticks))
        #print(json.dumps(lista_ticks,indent=2))
        for tick in lista_ticks:
            i = i + 1
            if "PERP" in str(tick["symbol"]):
                #print(tick["symbol"], i)
                ticks.append(str(tick["symbol"]))
        #print ("Cantidad de Monedas encontradas en par USDT:", len(ticks))
        return ticks
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT (buscar_ticks())")
        print(e)
        print("")
        return []
#-------------------------------------------------------------

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        # Precio actual para BINANCE
        return float(binance_client.ticker_price(symbol=symbol)[0]['price'])
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BINANCE")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Acondicionar el symbol
        symbol = symbol.upper()

        # Obtener el apalancamiento máximo
        brackets = binance_client.leverage_brackets(pair=symbol)
        for bracket in brackets:
            if bracket['symbol'] == symbol:
                return bracket['brackets'][0]['initialLeverage']
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BINANCE")
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
        binance_client.change_leverage(symbol=symbol, leverage=int(leverage))
    
    except Exception as e:
        print(f"ERROR CAMBIANDO EL APALANCAMIENTO DE {symbol} EN BINANCE")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE BINANCE NUEVA ORDEN 'LIMIT' , 'MARKET' o "CONDITIONAL"
# -----------------------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancameinto(symbol=symbol, leverage=leverage)

        # Define el lado para el modo hedge
        if side == "BUY":
            position_side = "LONG"
        if side == "SELL":
            position_side = "SHORT"

        # Definir la cantidad exacta que permite binance
        orden = binance_client.exchange_info()['symbols']
        for activo in orden:
            if activo['symbol'] == symbol:
                cantidad_paso = float(activo['filters'][1]['stepSize'])
        quantity = round(quantity/cantidad_paso)*cantidad_paso

        # Coloca la orden "LIMIT" , "MARKET" o "CONDITIONAL"
        if order_type == "LIMIT":
            order = binance_client.new_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=order_type,
                quantity=quantity,
                price=price,
                timeinforce="GTC",
                recvWindow=int(time.time()*1000),
            )
        if order_type == "MARKET":
            order = binance_client.new_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=order_type,
                quantity=quantity,
                recvWindow=int(time.time()*1000)
            )
        if order_type == "CONDITIONAL":
            order = binance_client.new_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type="STOP_MARKET",
                quantity=quantity,
                stopPrice=price,
                timeinforce="GTC",
                recvWindow=int(time.time()*1000),
            )
        #print(json.dumps(order,indent=2))
        print(f"Orden colocada en {order['price']}. ID:", order["orderId"])
        print((""))
        
        if order_type == "CONDITIONAL":
            price = order["stopPrice"]
        else:
            price = order["price"]

        return {
                "orderId": order["orderId"],
                "price": price,
                "qty": order["origQty"]
                }

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BINANCE")
        print(e)
        print("")
# -----------------------------------------------------------------

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:

        print("Cancelando todas las ordenes abiertas...")
        binance_client.cancel_open_orders(symbol=symbol, recvWindow=int(time.time()*1000))
        print("Ordenes abiertas canceladas")
        print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BINANCE")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        return binance_client.get_orders(symbol=symbol)

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS")
        print(e)
        print("")
        return []
# ----------------------------------------------------

# FUNCIÓN QUE BUSCA LA INFO DE TODAS LAS ORDENES CERRADAS
# -------------------------------------------------------
def obtener_historial_ordenes(symbol,limit=100):
    try:

        # Definir el limite de ordenes a buscar
        if limit > 100:
            limit = 100

        return binance_client.get_all_orders(symbol=symbol,limit=limit)
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN obtener_historial_ordenes() de BINANCE")
        print(e)
        print("")
# -------------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:

        print(f"Cancelando orden {orderId}")
        order = binance_client.cancel_order(symbol=symbol, orderId=orderId)
        print(f"Eliminada la orden {orderId} de {symbol.split('USD')[0]}.")
        print("")
        return order
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {id} DE BINANCE")
        print(e)
        print("")
# -----------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        posiciones = binance_client.get_position_risk(symbol=symbol)
        #print(json.dumps(posiciones,indent=2))
        lista = []
        for posicion in posiciones:
            if posicion['symbol'] == symbol and posicion['positionAmt'] != "0":
                lista.append(posicion)
        return lista

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BINANCE")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(symbol, positionSide):
    try:

        # Obtener posiciones
        posiciones = obtener_posicion(symbol)
        
        # Definir el lado segun la posición
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "SELL"
        if positionSide == positionSide.upper():
            side = "BUY"

        for posicion in posiciones:
            if posicion['positionSide'] == positionSide.upper():
                quantity = abs(float(posicion['positionAmt']))
                print(quantity)
            
        # Cerrar posición
        print("Cerrando posición...")
        order = binance_client.new_order(
                                    symbol=symbol, 
                                    side=side, 
                                    positionSide=positionSide, 
                                    type="MARKET",
                                    quantity=quantity, 
                                    timestamp=int(time.time()*1000)
                                    )
        print(f"Posición {positionSide} Cerrada")
        print("")
        return order

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BINANCE")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN STOP LOSS
# -------------------------------
def stop_loss(symbol, positionSide, stopPrice):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "SELL"
        if positionSide == "SHORT":
            side = "BUY"
        
        # Colocar la orden de Stop Loss
        orden = binance_client.new_order(
                                        symbol=symbol, 
                                        side=side, 
                                        positionSide=positionSide, 
                                        type="STOP_MARKET", 
                                        stopPrice=stopPrice, 
                                        closePosition=True,
                                        timestamp = int(time.time()*1000),
                                        )
        
        print(f"Stop Loss Colocado en {orden['stopPrice']}. ID:", orden["orderId"])
        print("")
        
        return {
                "orderId": orden["orderId"],
                "price": orden["stopPrice"],
                "qty": orden["origQty"]
                }
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN BINANCE")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type, tpSize=""):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        type = type.upper()
        if positionSide == "LONG":
            side = "SELL"
            quantity = str(tpSize)
            if tpSize == "":
                quantity = obtener_posicion(symbol=symbol)[0]['positionAmt']
        if positionSide == "SHORT":
            side = "BUY"
            quantity = str(tpSize)
            if tpSize == "":
                quantity = obtener_posicion(symbol=symbol)[1]['positionAmt']

        info = binance_client.exchange_info()['symbols']
        for data in info:
            if data['symbol'] == symbol:
                decimales_precio = len(data['filters'][0]['tickSize'].split(".")[-1])
                tickSize = float(data['filters'][0]['tickSize'])
                stopPrice = round(round(float(stopPrice)/tickSize)*tickSize, decimales_precio)
                decimales_moneda = len(data['filters'][1]['stepSize'].split(".")[-1])
                stepSize = float(data['filters'][1]['stepSize'])
                quantity = round(round(float(quantity)/stepSize)*stepSize,decimales_moneda)
                print("precio:", stopPrice, "cantidad:", quantity)

        # Colocar Take Profit Market
        if type == "MARKET":
            type = "TAKE_PROFIT_MARKET"
            orden = binance_client.new_order(
                                            symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide, 
                                            type=type, 
                                            stopPrice=float(stopPrice), 
                                            closePosition=True,
                                            timestamp = int(time.time()*1000)
                                            )
        
        # Colocar Take Profit Limit
        if type == "LIMIT":
            type = "TAKE_PROFIT"
            orden = binance_client.new_order(
                                            symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide, 
                                            type=type, 
                                            stopPrice=float(stopPrice),
                                            price=float(stopPrice),
                                            quantity=quantity,
                                            timestamp = int(time.time()*1000)
                                            )
        
        print(f"Take Profit Colocado en {orden['stopPrice']}. ID:", orden["orderId"])
        print("")
        
        return {
                "orderId": orden["orderId"],
                "price": orden["stopPrice"],
                "qty": orden["origQty"]
                }
    
    except Exception as e:
        print("ERROR COLOCANDO TAKE PROFIT EN BINANCE")
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
            side = "SELL"
            quantity = obtener_posicion(symbol=symbol)[0]['positionAmt']
        if positionSide == "SHORT":
            side = "BUY"
            quantity = str(float(obtener_posicion(symbol=symbol)[1]['positionAmt'])*(-1))
        
        # Colocar la orden de Trailing Stop
        orden = binance_client.new_order(
                                        symbol=symbol, 
                                        side=side, 
                                        positionSide=positionSide, 
                                        type="TRAILING_STOP_MARKET", 
                                        activationPrice=activationPrice,
                                        quantity=quantity,
                                        callbackRate=callbackRate,
                                        timestamp = int(time.time()*1000)
                                        )
        
        print(f"Trailing Stop Colocado en {orden['activatePrice']}. ID:", orden["orderId"])
        print("")
        
        return {
                "orderId": orden["orderId"],
                "price": orden["activatePrice"],
                "qty": orden["origQty"]
                }
    
    except Exception as e:
        print("ERROR COLOCANDO TRAILING STOP EN BINANCE")
        print(e)
        print("")
# -----------------------------------

# FUNCIÓN QUE OBTIENE EL MONTO DISPONIBLE DE LA CUENTA
# ----------------------------------------------------
def patrimonio(symbol):
    try:
        activos = binance_client.balance()
        for activo in activos:
            if activo['asset'] == symbol.split("USD")[0]:
                return float(activo['balance'])
    
    except Exception as e:
        print("ERROR OBTENIENDO EL PATRIMONIO ACTUAL")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE OBTIENE EL MARGEN DISPONIBLE
# ----------------------------------------
def margen_disponible(symbol):
    try:
        activos = binance_client.balance()
        for activo in activos:
            if activo['asset'] == symbol.split("USD")[0]:
                return float(activo['withdrawAvailable'])
    
    except Exception as e:
        print("ERROR OBTENIENDO EL MARGEN DISPONIBLE")
        print(e)
        print("")
# ----------------------------------------

#prueba = nueva_orden(symbol="ETHUSD_PERP", order_type="LIMIT", quantity=1, price=2560, side="BUY", leverage=9)
#prueba = apalancameinto_max("ETHUSD_PERP")
#prueba = obtener_historial_ordenes("BTCUSD_PERP")
#prueba = take_profit("ETHUSD_PERP","SHORT",2840,"LIMIT",1)
#print(json.dumps(prueba,indent=2))