import credenciales
from gate_api import ApiClient, Configuration, FuturesApi, FuturesOrder
import json
import time


# Definir la API de GATE.io
# Configuración
config = Configuration(
    key=credenciales.gateio_api_key,  # Reemplaza con tu API key
    secret=credenciales.gateio_api_secret  # Reemplaza con tu API secret
)
# Creación del cliente
with ApiClient(config) as api_client:
    futures_api = FuturesApi(api_client)
settle = "usdt"

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        precio = futures_api.get_futures_contract(settle="usdt", contract=symbol).last_price
        return float(precio)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN GATEIO")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE GATEIO NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Modificar el apalancamiento
        futures_api.update_dual_mode_position_leverage(settle, symbol, leverage)

        # Definir la cantidad por lote
        lote = float(futures_api.get_futures_contract(settle=settle, contract=symbol).quanto_multiplier)
        quantity = quantity/lote

        # Definir el lado
        if side == "SELL":
            quantity = -quantity
        
        tif = "gtc"
        if order_type == "MARKET":
            price = 0
            tif = "ioc"

        # Detalles de la orden LIMIT
        order = FuturesOrder(
            contract=symbol,    # Contrato de futuros, por ejemplo, BTC/USDT
            size=quantity,      # Cantidad de contratos a comprar/vender
            price=str(price),   # Precio límite
            tif=tif,            # 'gtc' para limit y 'ioc' para market
            reduce_only=False,  # Indica si es una orden de solo reducción
            is_close=False      # Indica si es una orden de cierre
        )
        
        # Colocar la orden LIMIT
        response = futures_api.create_futures_order(settle=settle, futures_order=order)
        #print(response)
        
        print(f"Orden colocada en {response.price}. ID:", response.id)
        print("")
    
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN GATEIO")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:
        
        print("Cancelando ordenes...")
        futures_api.cancel_futures_orders(contract=symbol,settle=settle)
        print("Se cancelaron todas las ordenes")
        print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE GATEIO")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        print("Buscando ordenes...")
        oredenes_abiertas = futures_api.list_futures_orders(settle=settle,status="open")
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
        futures_api.cancel_futures_order(settle=settle,order_id=orderId)
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

        posiciones = []
        ordenes = futures_api.list_positions(settle=settle)
        for orden in ordenes:
            if orden.open_time != 0:
                posiciones.append(orden)
        return posiciones

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE GATEIO")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(symbol, positionSide):
    try:
        positionSide = positionSide.upper()

        # Obtener las posiciones
        posiciones = obtener_posicion(symbol)
        for posicion in posiciones:
            if posicion.size > 0 and positionSide == "LONG":
                size = posicion.size*(-1)
            if posicion.size < 0 and positionSide == "SHORT":
                size = posicion.size*(-1)

        # Detalles de la orden LIMIT
        order = FuturesOrder(
                                id = 0,
                                user = 0,
                                create_time = 0,
                                finish_time = 0,
                                finish_as = "filled",
                                status = "open",
                                contract = symbol,
                                size = size,
                                iceberg = 0,
                                price = "0",
                                is_close = True,
                                reduce_only = True,
                                is_reduce_only = True,
                                is_liq = True,
                                tif = "ioc",
                                left = 0,
                                fill_price = "0"
                            ) 

        # Cerrar posición
        print("Cerrando posición...")
        print(futures_api.create_futures_order(settle=settle, futures_order=order))
        print(f"Posición Cerrada")
        print("")

    except Exception as e:
        print("ERROR CERRANDO POSICION EN GATEIO")
        print(e)
        print("")
# -------------------------------