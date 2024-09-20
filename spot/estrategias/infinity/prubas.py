import spot
import credenciales
from pybit.unified_trading import HTTP
from binance.spot import Spot
import json
import time


# Definir la session para Bybit
bybit_session = HTTP(
                    testnet=False,
                    api_key=credenciales.bybit_api_key,
                    api_secret=credenciales.bybit_api_secret,
                )

# API key/secret are required for user data endpoints
client = Spot(api_key=credenciales.binance_api_key, api_secret=credenciales.binance_api_secret)

#orden = client.account()['balances'][0]
#orden = spot.obtener_posicion("bybit", "ratsusdt")
#orden = spot.precio_actual_activo("BYBIT","rats")
#orden = spot.obtener_ordenes("binance","btc",orderId="")
#orden = spot.nueva_orden("BINANCE", "btc", "limit", 0.0001, 70000, "sell")
#orden = spot.obtener_historial_ordenes(exchange="binance", symbol="btc")
orden = spot.cancelar_orden("binance", "btc", "30563467154")
print(json.dumps(orden,indent=2))
