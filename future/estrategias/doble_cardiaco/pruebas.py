import traceback
import future
try:
    precio = future.precio_actual_activo(exchange="BINANCE", symbol="BTC")
    print(precio)
except Exception as e:
    # Capturar la excepción y obtener la información del traceback
    print("ERROR")
    print(e)
    traceback.print_exc()
