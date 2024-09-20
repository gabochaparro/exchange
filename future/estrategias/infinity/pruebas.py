import credenciales
import future
import json
from pybit.unified_trading import HTTP
import threading
import time



bybit_session = HTTP(
    testnet=False,
    api_key=credenciales.bybit_subcuenta04_api_key,
    api_secret=credenciales.bybit_subcuenta04_api_secret,
)

#orden = future.nueva_orden(exchange="BYBIT", symbol="1000rats", order_type="conditional", quantity=60, price=0.119, side="buy", leverage=200)
#orden = future.obtener_ordenes(exchange="BYBIT", symbol="1000rats", orderId="1aff609f-6a79-4691-aa9f-78be7b8ce181")
#orden = future.obtener_posicion(exchange="BYBIT", symbol="ordi")
#orden = future.take_profit(exchange="BYBIT", symbol="zeta", positionSide="LONG", stopPrice=0.7790, type="LIMIT")
#orden = future.stop_loss(exchange="BYBIT", symbol="1000rats", positionSide="short", stopPrice=0.09049)
#orden = future.obtener_historial_ordenes(exchange="BYBIT", symbol="1000rats")
#orden = future.patrimonio(exchange="BYBIT")
#print(json.dumps(orden,indent=2))

#parametros = json.load(open("future/estrategias/infinity/parametros_infinity_2.0.json", "r"))
#parametros['direccion'] = ""
#json.dump(parametros, open("future/estrategias/infinity/parametros_infinity_2.0.json", "w"), indent=4)
