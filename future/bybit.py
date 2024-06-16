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

# FUNCIÓN DE BYBIT NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        # Cambia el apalancamiento
        apalancamiento_actual = (bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if apalancamiento_actual != str(leverage):
            bybit_session.set_leverage(category="linear", symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))
            apalancamiento_actual = (bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
            #print("apalancamiento actual:", apalancamiento_actual)

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
def obtener_ordenes(symbol):
    try:

        print("Buscando ordenes...")
        oredenes_abiertas = bybit_session.get_open_orders(category="linear",symbol=symbol)["result"]['list']
        print(f"{len(oredenes_abiertas)} ordenes encontradas")
        return oredenes_abiertas

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BYBIT")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, id):
    try:
        
        print(f"Eliminando orden {id}...")
        bybit_session.cancel_order(category="linear",symbol=symbol,orderId=id)
        print(f"Eliminada la orden {id} de {symbol}.")
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