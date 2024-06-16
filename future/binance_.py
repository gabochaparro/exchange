
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

# FUNCIÓN DE BINANCE NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        # Cambia el apalancamiento
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
        print(f"Orden colocada en {order["price"]}. ID:", order["orderId"])
        print((""))

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
        print(binance_client.futures_cancel_all_open_orders(symbol=symbol, timestamp=time.time()))
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
def cancelar_orden(symbol, id):
    try:

        print(f"Cancelando orden {id}")
        binance_client.futures_cancel_order(symbol=symbol, orderId=id)
        print(f"Eliminada la orden {id} de {symbol}.")
        print("")
    
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
        print(json.dumps(binance_client.futures_create_order(
                                                            symbol=symbol, 
                                                            side=side, 
                                                            positionSide=positionSide, 
                                                            type="MARKET",
                                                            quantity=quantity, 
                                                            timestamp=time.time()
                                                            ),indent=2))
        print(f"Posición {positionSide} Cerrada")
        print("")

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BINANCE")
        print(e)
        print("")
# -------------------------------