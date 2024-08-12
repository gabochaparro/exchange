import credenciales
import future
import json
from pybit.unified_trading import HTTP
import threading
import time



bybit_session = HTTP(
    testnet=False,
    api_key=credenciales.bybit_api_key,
    api_secret=credenciales.bybit_api_secret,
)

#future.nueva_orden(exchange="BYBIT", symbol="XRP", order_type="LIMIT", quantity=10, price=0.5, side="BUY", leverage=200)
#orden = future.obtener_ordenes(exchange="BYBIT", symbol="zeta", orderId="35a06d77-1e23-47bd-97d9-fd34b9a4f9b3")
#orden = future.obtener_posicion(exchange="BYBIT", symbol="ordi")
#orden = future.take_profit(exchange="BYBIT", symbol="zeta", positionSide="LONG", stopPrice=0.7790, type="LIMIT")
orden = future.stop_loss(exchange="BYBIT", symbol="1000rats", positionSide="short", stopPrice=0.09049)
print(json.dumps(orden,indent=2))