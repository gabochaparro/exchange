import future_ws
import threading

threading.Thread(target=future_ws.precio_actual_activo, args=("bybit", "paxg")).start()
while True:
    precio_actual = future_ws.precio_actual
    while precio_actual == None:
        precio_actual = future_ws.precio_actual
    print(precio_actual)