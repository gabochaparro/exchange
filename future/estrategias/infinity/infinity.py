''' 
Grid de futuros que imita el comportamiento del grid spot infinity de BingX.
La gran diferencia es que puedes aprovechar el apalancamiento para aumentar las ganancias.
El riesgo aumenta a medidas que icrementas el apalancamiento (recomiendo 3x máximo).
Pudes quemar la cuenta si desconoces la magnitud de las correcciones mercado.
'''
import future
import json
import time

# Abrir el archivo parametros.json y cargar su contenido
parametros = json.load(open("future/estrategias/infinity/parametros.json", "r"))

# PARAMETROS DE LA ESTRATEGIA
# ---------------------------
activo = parametros['activo']                   # Activo a operar
apalancamiento = parametros['apalancamiento']   # Se recomienda un apalancamiento muy bajo para esta estrategia 
precio_minimo = parametros['precio_minimo']     # Por debajo del precio mínimo se mantiene la posición sin cambios
ganancia_grid = parametros['ganancia_grid']     # Distancia en porcentaje entre cada grilla
inversion = parametros['inversion']             # Inversión de la estrategia
tp = parametros['tp']                           # Take profit para detener la estrategia por completo
sl = parametros['sl']                           # Stop Loss para detener la estrategia por completo
exchange = parametros['exchange']               # Exchange a utilizar
# ---------------------------

precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
print("")
print(precio_actual)
decimales = len(str(precio_actual).split(".")[-1])
referencia = precio_minimo
grid = []
grid.append(referencia)
techo = 1.06
proxima_compra = 0
proxima_venta = 0

while True:
    
    precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)

    while grid[-1] < precio_actual:
        grid.append(round(referencia*(1+ganancia_grid/100),decimales))
        referencia = referencia*(1+ganancia_grid/100)
        
        if grid[-1] > precio_actual:
            print("")
            print("Grilla Actualizada:")
            print(grid)
            print("")
    
    for grilla in grid:
                if 100*abs(precio_actual - grilla)/precio_actual <= ganancia_grid and (precio_actual - grilla) > 0:
                    if proxima_compra != grilla:
                        proxima_compra = grilla
                        print("Proxima Compra", proxima_compra)
                        print(time.time())
                        print("")
                
                if 100*abs(grilla - precio_actual)/precio_actual <= ganancia_grid and (precio_actual - grilla) < 0:
                    if proxima_venta != grilla:
                        proxima_venta = grilla
                        print("Proxima Venta", proxima_venta)
                        print(time.time())
                        print("")