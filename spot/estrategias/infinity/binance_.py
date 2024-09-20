
import credenciales
from binance.spot import Spot
import json
import time


# API key/secret are required for user data endpoints
binance_client = Spot(
                    api_key=credenciales.binance_api_key, 
                    api_secret=credenciales.binance_api_secret
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
        return float(binance_client.ticker_price(symbol=symbol)['price']) #Busca la info de una moneda
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BINANCE")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE BINANCE NUEVA ORDEN 'LIMIT' , 'MARKET' o "CONDITIONAL"
# ------------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side):
    try:

        # Coloca la orden "LIMIT" , "MARKET" o "CONDICIONAL"
        if order_type.upper() == "LIMIT":
            params = {
                        'symbol': symbol,
                        'side': side,
                        'type': order_type,
                        'timeInForce': 'GTC',
                        'quantity': quantity,
                        'price': price
                    }
        
        if order_type.upper() == "MARKET":
            params = {
                        'symbol': symbol,
                        'side': side,
                        'type': order_type,
                        'quantity': quantity
                    }
        
        if order_type.upper() == "CONDITIONAL":
            params = {
                        'symbol': symbol,
                        'side': side,
                        'type': 'STOP_LOSS',
                        'quantity': quantity,
                        "stopPrice": price
                    }
            
        response = binance_client.new_order(**params)
        #print(json.dumps(response,indent=2))

        if order_type.upper() == "CONDITIONAL":
            response = obtener_ordenes(symbol=symbol, orderId=response["orderId"])
            price = response['stopPrice']
        else:
            price = response['price']

        print(f"Orden {order_type.upper()}-{side.upper()} de {response['origQty']}{symbol.split("USDT")[0]} colocada en {price}. ID:", response["orderId"])
        print((""))
        
        return {
                "orderId": response["orderId"],
                "price": float(price),
                "qty": float(response['origQty'])
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
        order = binance_client.cancel_open_orders(symbol=symbol, timestamp=time.time())
        print("Ordenes eliminadas")
        print("")
        return order
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BINANCE")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:

        print(f"Cancelando orden {orderId}")
        order = binance_client.cancel_order(symbol=symbol, orderId=orderId)
        print(f"Eliminada la orden {orderId} de {symbol}.")
        print("")
        return order
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {id} DE BINANCE")
        print(e)
        print("")
# -----------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol,orderId=""):
    try:
            
        if orderId == "":
            ordenes = binance_client.get_open_orders(symbol=symbol)
        
        if orderId != "":
            ordenes = binance_client.get_order(symbol=symbol,orderId=orderId)

        return ordenes

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES CERRADAS
# ----------------------------------------------------
def obtener_historial_ordenes(symbol, limit=30):
    try:
        return binance_client.get_orders(symbol=symbol, limit=limit,)

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BYBIT")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        if symbol.upper() == "USDT" or symbol.upper() == "USDTUSDT":
            symbol = "USDT"
        else:
            symbol = symbol.split("USDT")[0].upper()
        
        balances = binance_client.account()['balances']
        for balance in balances:
            if balance['asset'] == symbol:
                return float(balance['free'])

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BINANCE")
        print(e)
        print("")
# ---------------------------------------------

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
        
        print(f"Stop Loss Colocado en {orden['stopPrice']}. ID:", orden["orderId"])
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
        
        print(f"Take Profit Colocado en {orden['stopPrice']}. ID:", orden["orderId"])
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

#orden = nueva_orden("BTCUSDT", "CONDITIONAL", 0.0001, 60000, "BUY")
#orden = obtener_ordenes("BTCUSDT","30488978269")
#orden = obtener_historial_ordenes("BTCUSDT")
#orden = obtener_posicion("btcUSDT")
#print(json.dumps(orden,indent=2))