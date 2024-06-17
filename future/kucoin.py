import credenciales
from kucoin_futures.client import Trade, Market
import json
import time


# Definir la API de KuCoin
kucoin_trade_client = Trade(
                            key=credenciales.kucoin_api_key, 
                            secret=credenciales.kucoin_api_secret, 
                            passphrase=credenciales.kucoin_api_passphrase
                            )

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        precio = Market().get_contract_detail(symbol=symbol)['markPrice']
        return float(precio)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN KUCOIN")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE KUCOIN NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Definir la cantidad en lotes para poder colocar la orden
        lote = Market().get_contract_detail(symbol=symbol)['multiplier']
        quantity = quantity/lote
        
        # Colocar la orden segun el tipo
        side = side.lower()
        if order_type == "LIMIT":
            order = kucoin_trade_client.create_limit_order(
                                                        symbol=symbol,
                                                        side=side,
                                                        lever=leverage,
                                                        size=quantity,
                                                        price=price,
                                                    )
            
        if order_type == "MARKET":
            order = kucoin_trade_client.create_market_order(
                                                        symbol=symbol,
                                                        side=side,
                                                        lever=leverage,
                                                        size=quantity,
                                                    )
    
        print(f"Orden colocada en {price}. ID:", order["orderId"])
        print("")

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN KUCOIN")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:
        
        print("Cancelando ordenes...")
        kucoin_trade_client.cancel_all_limit_order(symbol=symbol)
        kucoin_trade_client.cancel_all_stop_order(symbol=symbol)
        print("Se cancelaron todas las ordenes")
        print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE KUCOIN")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        print("Buscando ordenes...")
        oredenes_abiertas = kucoin_trade_client.get_order_list(symbol=symbol, status="active")['items']
        print(f"{len(oredenes_abiertas)} ordenes encontradas")
        return oredenes_abiertas

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN KUCOIN")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:
        
        print(f"Eliminando orden {orderId}...")
        kucoin_trade_client.cancel_order(orderId=orderId)
        print(f"Eliminada la orden {orderId} de {symbol}.")
        print("")
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {id} DE KUCOIN")
        print(e)
        print("")
# -----------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        return kucoin_trade_client.get_position_details(symbol=symbol)

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE KUCOIN")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(symbol):
    try:
            
        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(kucoin_trade_client.create_market_order(
                                                        symbol=symbol,
                                                        closeOrder="TRUE",
                                                        side="",
                                                        lever=""
                                                    ),indent=2))
        
        print(f"Posición Cerrada")
        print("")

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BYBIT")
        print(e)
        print("")
# -------------------------------