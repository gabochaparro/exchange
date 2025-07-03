import inverse_ws
import threading

threading.Thread(target=inverse_ws.precio_actual_activo, args=("BYBIT", "ada")).start()
print("ESPERANDO EL PRECIO ACTUAL...")
while True:
    precio_actual = inverse_ws.precio_actual
    while precio_actual == None:
        precio_actual = inverse_ws.precio_actual
    print(precio_actual)