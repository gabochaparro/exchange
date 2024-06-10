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


# FUNCIÓN DE GATEIO NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Modificar el apalancamiento
        futures_api.update_dual_mode_position_leverage('usdt', symbol, leverage)

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
        response = futures_api.create_futures_order('usdt', order)
        #print(response)
        
        print(f"Orden colocada en {response.price}. ID:", response.id)
        print("")
    
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN GATEIO")
        print(e)
        print("")
# ------------------------------------------------