import credenciales
import pybitget
import json
import time


# Definir el cliente para BitGet
bitget_client = pybitget.Client(
                            api_key=credenciales.bitget_api_key, 
                            api_secret_key=credenciales.bitget_api_secret, 
                            passphrase = credenciales.bitget_api_passphrase, 
                            use_server_time=False,
                        )

# Parametros Generales
marginCoin = "USDT"
productType = "umcbl"

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        precio = bitget_client.mix_get_single_symbol_ticker(symbol=symbol)['data']['last']
        return float(precio)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BITGET")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE BITGET NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:

        # Modificar apalancamiento
        bitget_client.mix_adjust_leverage(symbol=symbol, marginCoin=marginCoin, leverage=leverage, holdSide=None)

        # Definir el lado
        if side == "BUY":
            side = "OPEN_LONG"
        if side == "SELL":
            side = "OPEN_SHORT"

        # Colocar la orden
        order = bitget_client.mix_place_order(
                                        symbol=symbol, 
                                        marginCoin=marginCoin, 
                                        size=quantity,
                                        side=side, 
                                        orderType=order_type, 
                                        price=price
                                    )
        
        print(f"Orden colocada en {price}. ID:", order["data"]["orderId"])
        print("")

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BITGET")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        print("Buscando ordenes...")
        ordenes_abiertas = bitget_client.mix_get_open_order(symbol=symbol)['data']
        print(f"{len(ordenes_abiertas)} ordenes encontradas")
        return ordenes_abiertas

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
        ordenes_abiertas = obtener_ordenes(symbol)
        for orden in ordenes_abiertas:
            bitget_client.mix_cancel_order(symbol=symbol, marginCoin=marginCoin, orderId=orden['orderId'])
        
        print("Se cancelaron todas las ordenes")
        print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BYBIT")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, id):
    try:
        
        print(f"Eliminando orden {id}...")
        bitget_client.mix_cancel_order(symbol=symbol,marginCoin=marginCoin,orderId=str(id))
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

        return bitget_client.mix_get_single_position(symbol=symbol,marginCoin=marginCoin)['data']

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
            side = "close_long"
        if positionSide == "SHORT":
            side = "close_short"
            
        # Obtener cantidad
        cantidad = obtener_posicion(symbol)[0]['available']

        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(bitget_client.mix_place_order(
                                        symbol=symbol, 
                                        marginCoin=marginCoin, 
                                        size=cantidad,
                                        side=side, 
                                        orderType="MARKET", 
                                        price=0
                            ),indent=2))
        
        print(f"Posición {positionSide} Cerrada")
        print("")

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BYBIT")
        print(e)
        print("")
# -------------------------------