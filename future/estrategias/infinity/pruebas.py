import credenciales
import future
import json
from pybit.unified_trading import HTTP


session = HTTP(
    testnet=False,
    api_key=credenciales.bybit_api_key,
    api_secret=credenciales.bybit_api_secret,
)


#print(json.dumps(session.get_order_history(category="linear",symbol="MYROUSDT",limit=3,)['result']['list'],indent=2))

#ordenes_abierta = future.obtener_ordenes(exchange="bybit", symbol="myro")
#print(json.dumps(ordenes_abierta, indent=2))

orden = future.nueva_orden(exchange="BYBIT", symbol="ustc", order_type="LIMIT", quantity=300, price=0.019, side="BUY",leverage=100)
print(orden)