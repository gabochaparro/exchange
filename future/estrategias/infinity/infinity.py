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
apalancamiento = parametros['apalancamiento']   # Se recomienda un apalancamiento muy bajo para esta estrategia (<=3x)
precio_minimo = parametros['precio_minimo']     # Por debajo del precio mínimo se mantiene la posición sin cambios
ganancia_grid = parametros['ganancia_grid']     # Distancia en porcentaje entre cada grilla
inversion = parametros['inversion']             # Inversión de la estrategia
tp = parametros['tp']                           # Take profit para detener la estrategia por completo
sl = parametros['sl']                           # Stop Loss para detener la estrategia por completo
exchange = parametros['exchange']               # Exchange a utilizar
# ---------------------------



# Función que actualiza el grid
# -----------------------------
def actualizar_grid(referencia, decimales):
    
    # Consultar precio actual
    precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)

    # Ciclo que arma y actualiza el grid
    while grid[-1] < precio_actual:
        grid.append(round(referencia*(1+ganancia_grid/100),decimales))
        referencia = round(referencia*(1+ganancia_grid/100),decimales)
        
        if grid[-1] > precio_actual:
            print("")
            print("Grilla Actualizada:")
            print(grid)
            print("")
    
    return grid
# -----------------------------

# Función  que  coloca las ordenes de compra
# -------------------------------------------
def ordenes_compra(exchange, symbol, qty):

    #Variable gobal
    global parejas_compra_venta, grid
    
    # Recorrer el grid
    for grilla in grid:
        if grilla < precio_actual < grilla*(1+ganancia_grid/100):
            precio_compra = grilla
        if grilla > precio_actual > grilla*(1-ganancia_grid/100):
            precio_venta = grilla
    
    # Verificar si la pareja compra_venta esta activa
    compra_activa = False
    for compra_venta in parejas_compra_venta:
        if compra_venta["compra"]['price'] == precio_compra and compra_venta["venta"]['ejecutada'] == False:
            compra_activa = True
    
    # Colocar la orden de compra y crear la pareja de compra_veta
    if not(compra_activa):
        orden = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=precio_compra, side="BUY", leverage=apalancamiento)
        parejas_compra_venta.append({"compra": {
                                        "orderId": orden['orderId'],
                                        "price": precio_compra,
                                        "ejecutada": False,
                                        "fecha_ejecucion" : 0
                                        },
                            "venta": {
                                        "orderId": "",
                                        "price": precio_venta,
                                        "ejecutada": False,
                                        "fecha_ejecucion" : 0
                            }})

# -------------------------------------------

# Funció que coloca lsa ordenes de venta
# --------------------------------------
def ordenes_venta(grid):
    pass
# --------------------------------------

# Inicializar las variables
precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
print("")
print(activo)
print(precio_actual)
decimales = len(str(precio_actual).split(".")[-1])
referencia = precio_minimo
grid = []
grid.append(referencia)
proxima_compra = 0
proxima_venta = 0
parejas_compra_venta = []
grid = actualizar_grid(referencia=referencia, decimales=decimales)
qty = round((inversion/(len(grid)-1)/precio_actual),decimales)
for grilla in grid:
    if grilla < precio_actual < grilla*(1+ganancia_grid/100):
        precio_compra = grilla
    if grilla > precio_actual > grilla*(1-ganancia_grid/100):
        precio_venta = grilla
orden = future.nueva_orden(exchange=exchange, symbol=activo, order_type="LIMIT", quantity=qty, price=precio_compra, side="BUY", leverage=apalancamiento)
parejas_compra_venta.append({"compra": {
                                "orderId": orden['orderId'],
                                "price": precio_compra,
                                "ejecutada": False,
                                "fecha_ejecucion" : 0
                                },
                    "venta": {
                                "orderId": "",
                                "price": precio_venta,
                                "ejecutada": False,
                                "fecha_ejecucion" : 0
                    }})


while True:
    
    # Actualizar el grid
    grid = actualizar_grid(referencia=referencia, decimales=decimales)
    
    # Consultar Precio Actual
    precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
    
    # Recorrer el Grid
    for grilla in grid:
        
        # Verificar que grilla es la proxima compra
        if 100*abs(precio_actual - grilla)/precio_actual <= ganancia_grid and (precio_actual - grilla) > 0:
            if proxima_compra != grilla:
                proxima_compra = grilla
                print("Proxima Compra", proxima_compra)
                print(time.time())
                print("")
        
        # Verificar que grilla es la proxima venta
        if 100*abs(grilla - precio_actual)/precio_actual <= ganancia_grid and (precio_actual - grilla) < 0:
            if proxima_venta != grilla:
                proxima_venta = grilla
                print("Proxima Venta", proxima_venta)
                print(time.time())
                print("")
