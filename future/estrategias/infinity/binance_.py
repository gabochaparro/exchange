
import credenciales
from binance.client import Client
import json
import time


# Definir el cliente para Binance
binance_client = Client(
                            api_key=credenciales.binance_api_key,
                            api_secret=credenciales.binance_api_secret,
                            tld="com"
                        )

# FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT
#------------------------------------------------------
def buscar_ticks():
    try:
        i = 0
        ticks =[]
        lista_ticks = binance_client.futures_symbol_ticker() #Buscar todos los pares de monedas
        #print ("Cantidad de Monedas encontradas en todos los pares:", len(lista_ticks))
        for tick in lista_ticks:
            i = i + 1
            if "USDT" in str(tick["symbol"]):
                #print(tick["symbol"], i)
                ticks.append(str(tick["symbol"]))
        #print ("Cantidad de Monedas encontradas en par USDT:", len(ticks))
        return ticks
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT (buscar_ticks())")
        print(e)
        e = "error"
        print("")
        ticks = []
        return ticks
#-------------------------------------------------------------

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        # Precio actual para BINANCE
        info = binance_client.futures_ticker(symbol=symbol) #Busca la info de una moneda
        return float(info["lastPrice"])
    
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

        # Obtener el apalancamiento máximo
        max_leverage = binance_client.futures_leverage_bracket(symbol=symbol)[0]['brackets'][0]['initialLeverage']
        return int(max_leverage)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BINANCE")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE BINANCE NUEVA ORDEN 'LIMIT' , 'MARKET' o "CONDITIONAL"
# ------------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        binance_client.futures_change_leverage(symbol=symbol, leverage=leverage)

        # Define el lado para el modo hedge
        if side == "BUY":
            position_side = "LONG"
        if side == "SELL":
            position_side = "SHORT"

        # Coloca la orden "LIMIT" o "MARKET"
        if order_type == "LIMIT":
            order = binance_client.futures_create_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=order_type,
                quantity=quantity,
                price=price,
                timeinforce="GTC",
                timestamp=time.time()
            )
        if order_type == "MARKET":
            order = binance_client.futures_create_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=order_type,
                quantity=quantity,
                timestamp=time.time()
            )
        print(f"Orden colocada en {order['price']}. ID:", order["orderId"])
        print((""))
        
        return {
                "orderId": order["orderId"],
                "price": order["price"]
                }

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BINANCE")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:

        print("Cancelando ordenes...")
        order = binance_client.futures_cancel_all_open_orders(symbol=symbol, timestamp=time.time())
        print(order)
        print("")
        return order
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BINANCE")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        print("Buscando ordenes...")
        ordenes = binance_client.futures_get_open_orders(symbol=symbol)
        print(f"{len(ordenes)} ordenes encontradas.")
        print("")
        return ordenes

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:

        print(f"Cancelando orden {orderId}")
        order = binance_client.futures_cancel_order(symbol=symbol, orderId=orderId)
        print(f"Eliminada la orden {orderId} de {symbol}.")
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

        return binance_client.futures_position_information(symbol=symbol)

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BINANCE")
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
            side = "SELL"
            quantity = float(obtener_posicion(symbol)[0]['positionAmt'])
        if positionSide == "SHORT":
            side = "BUY"
            quantity = float(obtener_posicion(symbol)[1]['positionAmt'])*(-1)
            
        # Cerrar posición
        print("Cerrando posición...")
        order = binance_client.futures_create_order(
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
        orden = binance_client.futures_create_order(
                                                    symbol=symbol, 
                                                    side=side, 
                                                    positionSide=positionSide, 
                                                    type="STOP_MARKET", 
                                                    stopPrice=stopPrice, 
                                                    closePosition=True,
                                                    timestamp = int(time.time()*1000)
                                                    )
        
        print(f"Stop Loss Colocado en {orden["stopPrice"]}. ID:", orden["orderId"])
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN BINANCE")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        type = type.upper()
        if positionSide == "LONG":
            side = "SELL"
            quantity = obtener_posicion(symbol=symbol)[0]['positionAmt']
        if positionSide == "SHORT":
            side = "BUY"
            quantity = str(float(obtener_posicion(symbol=symbol)[1]['positionAmt'])*(-1))

        # Colocar Take Profit Market
        if type == "MARKET":
            type = "TAKE_PROFIT_MARKET"
            orden = binance_client.futures_create_order(
                                                        symbol=symbol, 
                                                        side=side, 
                                                        positionSide=positionSide, 
                                                        type=type, 
                                                        stopPrice=stopPrice, 
                                                        closePosition=True,
                                                        timestamp = int(time.time()*1000)
                                                        )
        
        # Colocar Take Profit Limit
        if type == "LIMIT":
            type = "TAKE_PROFIT"
            orden = binance_client.futures_create_order(
                                                        symbol=symbol, 
                                                        side=side, 
                                                        positionSide=positionSide, 
                                                        type=type, 
                                                        stopPrice=stopPrice,
                                                        price=stopPrice,
                                                        quantity=quantity,
                                                        timestamp = int(time.time()*1000)
                                                        )
        
        print(f"Take Profit Colocado en {orden["stopPrice"]}. ID:", orden["orderId"])
        print("")
        return orden
    
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
        orden = binance_client.futures_create_order(
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
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO TRAILING STOP EN BINANCE")
        print(e)
        print("")
# -----------------------------------

#prueba = precio_actual_activo("1000RATSUSDT")
#print(json.dumps(prueba,indent=2))