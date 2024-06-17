import credenciales
from okx import Trade, Account, PublicData, MarketData
import json
import time

# Definir la API de OKX
tradeAPI = Trade.TradeAPI(credenciales.okx_api_key, 
                              credenciales.okx_api_secret, 
                              credenciales.okx_api_passphrase, 
                              False, 
                              "0"
                              )
accountAPI = Account.AccountAPI(credenciales.okx_api_key, 
                              credenciales.okx_api_secret, 
                              credenciales.okx_api_passphrase, 
                              False, 
                              "0"
                              )
instType = "SWAP"

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        precio = MarketData.MarketAPI(flag="0").get_ticker(instId=symbol)['data'][0]['last']
        return float(precio)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN OKX")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE OKX NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Definir la cantidad segun el tamaño del lote
        tickes = PublicData.PublicAPI(flag="0").get_instruments(instType=instType)['data']
        for tick in tickes:
            if tick['instId'] == symbol:
                lote = float(tick['ctVal'])
                quantity = quantity/lote

        # Definir la posicion segun el lado
        if side == "BUY":
            posSide = "long"
        if side == "SELL":
            posSide = "short"
        
        # Ajustar el apalancamiento
        print("")
        accountAPI.set_leverage(
                                    instId=symbol,
                                    lever=str(leverage),
                                    mgnMode="cross"
                                )
        print("")

        # Colocar la orden
        order = tradeAPI.place_order(
                                        instId=symbol,
                                        tdMode="cross",
                                        side=side.lower(),
                                        posSide=posSide,
                                        ordType=order_type.lower(),
                                        px=str(price),
                                        sz=str(quantity)
                                    )
        print("")
        
        if order["code"] == "0":
            print(f"Orden colocada en {price}. ID:", order["data"][0]["ordId"])
            print("")
        else:
            print("ERROR COLOCANDO LA ORDEN EN OKX, error_code = ",order["data"][0]["sCode"], ", Error_message = ", order["data"][0]["sMsg"])
            print("")
    
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN OKX")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        print("Buscando ordenes...")
        oredenes_abiertas = tradeAPI.get_order_list(instId=symbol, instType=instType,)['data']
        print(f"{len(oredenes_abiertas)} ordenes encontradas")
        return oredenes_abiertas

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN OKX")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:
        
        print(f"Eliminando orden {orderId}...")
        tradeAPI.cancel_order(instId=symbol, ordId=str(orderId),)
        print(f"Eliminada la orden {orderId} de {symbol}.")
        print("")
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {id} DE OKX")
        print(e)
        print("")
# -----------------------------

# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:
        
        print("Cancelando ordenes...")
        ordenes_abiertas = obtener_ordenes(symbol)
        if len(ordenes_abiertas) > 0:
            for orden in ordenes_abiertas:
                ordId = orden['ordId']
                cancelar_orden(symbol, ordId)
            print("Se cancelaron todas las ordenes")
            print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE OKX")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        return accountAPI.get_positions(instType=instType, instId=symbol)

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
        positionSide = positionSide.lower()
            
        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(tradeAPI.close_positions(
                                                    instId=symbol,
                                                    mgnMode="cross",
                                                    posSide=positionSide,
                                                  ),indent=2))
        
        print(f"Posición {positionSide} Cerrada")
        print("")

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BYBIT")
        print(e)
        print("")
# -------------------------------