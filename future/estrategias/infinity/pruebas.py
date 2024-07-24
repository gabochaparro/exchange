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
orden = future.obtener_ordenes(exchange="BYBIT", symbol="1000floki", orderId="495e195c-a47c-4907-a157-58b122155fbd")
#orden = bybit_session.get_order_history(category="linear",limit=30,)
#orden = future.nueva_orden(exchange="BYBIT", symbol="GODS", order_type="LIMIT", quantity=14, price=0.38, side="BUY", leverage=10)
#orden = future.take_profit(exchange="BYBIT", symbol="1000000PEIPEI", positionSide="LONG", stopPrice=0.368, type="LIMIT", tpSize="16")
print(json.dumps(orden,indent=2))