import credenciales
import future
import json
from pybit.unified_trading import HTTP
from binance.client import Client
import threading
import time
import shutil


bybit_session = HTTP(
                        testnet=False,
                        api_key=credenciales.bybit_subcuenta04_api_key,
                        api_secret=credenciales.bybit_subcuenta04_api_secret,
                    )

binance_client = Client(
                            api_key=credenciales.binance_api_key,
                            api_secret=credenciales.binance_api_secret,
                            tld="com"
                        )

# Obeter el tamaño y precio de la posicón
posiciones = future.obtener_posicion(exchange="BYBIT", symbol="1000rats")

for posicion in posiciones:

    # LONG-SHORT
    if posicion['positionIdx'] == 0:
        if posicion['liqPrice'] != "":
            precio_liquidacion = float(posicion['liqPrice'])
            print("Precio de liquidación unidireccional", precio_liquidacion)
            print("")

    # LONG
    if posicion['positionIdx'] == 1:
        if posicion['liqPrice'] != "":
            precio_liquidacion_long = float(posicion['liqPrice'])
            print("Precio de liquidación long", precio_liquidacion_long)
            print("")
        
    # SHORT
    if posicion['positionIdx'] == 2:
        if posicion['liqPrice'] != "":
            precio_liquidacion_short = float(posicion['liqPrice'])
            print("Precio de liquidación short", precio_liquidacion_short)
            print("")
