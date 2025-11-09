import time, numpy as np, talib, os, json
from pybit.unified_trading import WebSocket, HTTP

api_key = "tewcE5afHgDUDwByAy"
api_secret = "josg79vVzz5fzwcFK4QqLqCbIPzGeR0zBVBi"
bybit_session = HTTP(testnet=False, api_key=api_key, api_secret=api_secret)

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(category, symbol, orderId=""):
    try:
        return bybit_session.get_open_orders(category=category,symbol=symbol.upper(),orderId=orderId)["result"]['list']

    except Exception as e:
        print("ERROR")
# ----------------------------------------------------

print(json.dumps(obtener_ordenes("inverse", "BTCUSD"), indent=2))