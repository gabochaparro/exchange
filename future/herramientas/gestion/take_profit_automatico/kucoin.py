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

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Obtener el apalancamiento máximo
        max_leverage = Market().get_contract_detail(symbol=symbol)['maxLeverage']
        return int(max_leverage)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN KUCOIN")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE KUCOIN NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Definir la cantidad en lotes para poder colocar la orden
        lote = Market().get_contract_detail(symbol=symbol)['multiplier']
        quantity = quantity/lote
        
        # Controlar el apalancamiento
        max_leverage = apalancameinto_max(symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        
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

        return {
                "orderId": order["orderId"],
                "price": price
                }

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

# FUNCIÓN QUE COLOCA UN STOP LOSS
# -------------------------------
def stop_loss(symbol, positionSide, stopPrice):
    try:

        # Definir parametros
        positionSide = positionSide.lower()
        if positionSide == "long":
            side = "sell"
            stop="down"
        if positionSide == "short":
            side = "buy"
            stop="up"
        
        # Colocar la orden de Stop Loss
        orden = kucoin_trade_client.create_market_order(
                                                        symbol=symbol,
                                                        side=side,
                                                        type="market",
                                                        closeOrder=True,
                                                        stopPrice=str(stopPrice),
                                                        lever=0,
                                                        stop=stop,
                                                        stopPriceType="IP"
                                                        )
        
        print(f"Stop Loss Colocado {orden}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN KUCOIN")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type):
    try:

        # Definir parametros
        type = type.lower()
        positionSide = positionSide.lower()
        if positionSide == "long":
            side = "sell"
            stop="up"
        if positionSide == "short":
            side = "buy"
            stop="down"
        
        # Colocar la orden de Stop Loss
        orden = kucoin_trade_client.create_limit_order(
                                                        symbol=symbol,
                                                        side=side,
                                                        type=type,
                                                        closeOrder=True,
                                                        price=str(stopPrice),
                                                        stopPrice=str(stopPrice),
                                                        lever=0,
                                                        stop=stop,
                                                        stopPriceType="TP",
                                                        size=0
                                                        )
        
        print(f"Take Profit Colocado {orden}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO TAKE PROFIT EN BYBIT")
        print(e)
        print("")
# ------------------------------------------------