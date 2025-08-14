import future_ws
import inverse_ws
import threading
import time

hilo = threading.Thread(target=inverse_ws.precio_actual_activo, args=("bybit", "sol"), daemon=True)
hilo.start()

while True:
    print(inverse_ws.precio_actual)
    time.sleep(1)