import bybit.bybit_ws as bybit_ws
import asyncio
import threading
import time

ClasePresiosActuales = bybit_ws.PreciosActuales()

def iniciar_precio_actual():
    asyncio.run(ClasePresiosActuales.precio_actual("INVERSE", (["BTCUSd", "ethusd"])))

hilo = threading.Thread(target=iniciar_precio_actual, daemon=True)
hilo.start()

while True:
    if  not hilo.is_alive:
        hilo = threading.Thread(target=iniciar_precio_actual, daemon=True)
        hilo.start()
    print("Precio actual:", ClasePresiosActuales.precios_actuales)