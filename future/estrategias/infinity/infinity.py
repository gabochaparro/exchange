''' 
Grid de futuros que imita el comportamiento del grid spot infinity de BingX.
La gran diferencia es que puedes aprovechar el apalancamiento para aumentar las ganancias.
El riesgo aumenta a medidas que icrementas el apalancamiento (recomiendo 3x máximo).
Pudes quemar la cuenta si desconoces la magnitud de las correcciones mercado.
'''
import future
import future_ws
import json
import time
import threading

# Abrir el archivo parametros.json y cargar su contenido
parametros = json.load(open("future/estrategias/infinity/parametros.json", "r"))

# PARAMETROS DE LA ESTRATEGIA
# ---------------------------
exchange = parametros['exchange']               # Exchange a utilizar
activo = parametros['activo']                   # Activo a operar
apalancamiento = parametros['apalancamiento']   # Se recomienda un apalancamiento muy bajo para esta estrategia (<=3x)
precio_minimo = parametros['precio_minimo']     # Por debajo del precio mínimo se mantiene la posición sin cambios
ganancia_grid = parametros['ganancia_grid']     # Distancia en porcentaje entre cada grilla
cuenta = parametros['monto_cuenta']             # Inversión de la estrategia
tp = parametros['tp']                           # Take profit para detener la estrategia por completo
sl = parametros['sl']                           # Stop Loss para detener la estrategia por completo
# ---------------------------


# Función que actualiza el grid
# -----------------------------
def actualizar_grid():
    try:
        # variables globales
        global precio_actual

        while True:
            if iniciar_estrategia == True:
                # Consultar precio actual
                precio_actual = future_ws.precio_actual

            # Ciclo que arma y actualiza el grid
            referencia = grid[-1]
            while grid[-1] <= precio_actual:
                
                # Agregar un nuevo nivel al grid
                grid.append(round(referencia*(1+ganancia_grid/100),decimales_precio))
                referencia = grid[-1]
                
                # Consultar precio actual
                if iniciar_estrategia == True:
                    precio_actual = future_ws.precio_actual
                
                # Grilla actualizada
                if grid[-1] > precio_actual and iniciar_estrategia == True:
                    print("")
                    print("Grilla Actualizada.")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")
            time.sleep(0.3)
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN actualizar_grid()")
        print(e)
        print("")
# -----------------------------

# Función que verifica todos los parametros
# -----------------------------------------
def parametros():
    try:
        # Variables globales
        global apalancamiento, multiplo

        # Inversión Mínima
        inversion_minima = 5*(len(grid))

        # Revisar el apalancamiento
        if apalancamiento > future.apalancamiento_max(exchange=exchange,symbol=activo):
            apalancamiento = future.apalancamiento_max(exchange=exchange,symbol=activo)

        # Cantidad de cada compra en USDT
        while len(grid)-1 == 0:
            pass
        cantidad_usdt = round(cuenta*apalancamiento/(len(grid)-1), 2)

        # Cantidad de la 1ra posicion a colocar
        cantidad_monedas = round((cantidad_usdt/precio_actual), decimales_moneda)
        if multiplo >= 10:
            cantidad_monedas = round(cantidad_monedas/multiplo)*multiplo

        # Obtener el precio de la proxima compra y la proxima venta
        precio_compra, precio_venta = prox_compra_venta(grid)

        # Revisar el apalancamiento
        if apalancamiento > future.apalancamiento_max(exchange=exchange,symbol=activo):
            apalancamiento = future.apalancamiento_max(exchange=exchange,symbol=activo)
        
        # Imprimir Parametros
        print("-----------------------------------------")
        print("Exchange:", exchange.upper())
        print( "Activo:", activo.upper())
        print("Inversión mínima:", inversion_minima, "USDT")
        print("Rango mínimo:", precio_minimo, "USDT")
        print("Rango máximo: INFINITO")
        print("Cantidad de grids:", len(grid))
        print("Cantidad de cada compra:", cantidad_usdt, "USDT")
        print(f"Ganancias por cada grid: {ganancia_grid}%")
        print("Inversión inicial:", cuenta*apalancamiento, "USDT")
        print("Cuenta:", cuenta, "USDT")
        print(f"Apalancamiento: {apalancamiento}x")
        print("")
        print("Precio actual:", precio_actual, "USDT")
        print("Proxima compra:", precio_compra, "USDT")
        print("Próxima venta:", precio_venta, "USDT")
        print("Primera compra:", cantidad_monedas, activo.upper(), f"({cantidad_usdt} USDT)")
        print("-----------------------------------------")
        print("")

        # Detener estrategia por fondos insuficientes
        if cantidad_usdt <= 5 and cuenta*apalancamiento < inversion_minima:
            print("FONDOS INSUFICIENTES!")
            print("")
            exit()
        
        # Pedir confirmación para iniciar estrategia
        iniciar_estrategia = "*"
        while iniciar_estrategia != "":
            iniciar_estrategia = input("Presiona ENTER para iniciar la estrategia")
        if iniciar_estrategia == "":
            return cantidad_usdt
        
    except Exception as e:
        print("ERROR EN LA FUNCIÓN parametros()")
        print(e)
        print("")
        exit()
# -----------------------------------------

# FUnción que se encarga de entrar la próxima compra y la próxima venta
# ---------------------------------------------------------------------
def prox_compra_venta(grid):
    try:
        # Variables globales
        global precio_actual

        # Cosultar el precio actual
        if iniciar_estrategia == True:
            precio_actual = future_ws.precio_actual
        
        # Recorrer el grid y encontrar el próximo precio de compra y venta
        prox_compra = 0
        prox_venta = 0
        while prox_compra == 0 or prox_venta == 0:
            for grilla in grid:
                if grilla < precio_actual < grilla*(1+ganancia_grid/100):
                    prox_compra = grilla
                if grilla > precio_actual > grilla*(1-ganancia_grid/100):
                    prox_venta = grilla
            
                # Cosultar el precio actual
                if iniciar_estrategia == True:
                    precio_actual = future_ws.precio_actual

        return prox_compra, prox_venta
    
    except Exception as e:
        print("ERROR EN prox_compra_venta()")
        print(e)
        print("")
# ---------------------------------------------------------------------

# Función que actualiza el estado de las parejas de compra y venta
# ----------------------------------------------------------------
def actualizar_pareja(exchange, symbol):
    try:
        for pareja in parejas_compra_venta:
            # BYBIT
            if exchange.upper() == "BYBIT":
                # Obtener la orden de compra en BYBIT
                ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['compra']['orderId'])
                if ordenes != None:
                    if ordenes[0]['orderStatus'] == "Filled" and pareja['compra']['ejecutada'] == False:
                        pareja['compra']['ejecutada'] = True
                        print("Grid Actual:")
                        print(grid)
                        print("Cantidad de grillas:", len(grid))
                        print(json.dumps(parejas_compra_venta,indent=2))
                        print("")
                
                # Obtener la orden de venta en BYBIT
                if pareja['venta']['orderId'] != "":
                    ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['venta']['orderId'])
                    if ordenes != None:
                        if ordenes[0]['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                            pareja['venta']['ejecutada'] = True
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            print(json.dumps(parejas_compra_venta,indent=2))
                            print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCION actualizar_pareja()")
        print(e)
        print("")
# ----------------------------------------------------------------

# Función que coloca las ordenes de compra
# -------------------------------------------
def ordenes_compra(exchange, symbol, posicion_usdt, grid):
    try:
        while True:
            # Consultar precio actual
            precio_actual = future_ws.precio_actual

            # Obtener el precio de la proxima compra y la proxima venta
            prox_compra, prox_venta = prox_compra_venta(grid)

            # Verificar si la pareja compra_venta esta activa
            actualizar_pareja(exchange=exchange, symbol=symbol)
            compra_activa = False
            for compra_venta in parejas_compra_venta:
                if compra_venta["compra"]['price'] == prox_compra and compra_venta["venta"]['ejecutada'] == False:
                    compra_activa = True
            
            # Cantidad de cada compra
            qty = round((posicion_usdt/precio_actual),decimales_moneda)
            if multiplo >= 10:
                qty = round(qty/multiplo)*multiplo
            
            # Colocar la orden de compra y crear la pareja de compra_veta
            if not(compra_activa):
                orden = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_compra, side="BUY", leverage=apalancamiento)
                if orden != None:
                    parejas_compra_venta.append({
                                                "compra": {
                                                            "orderId": orden['orderId'],
                                                            "price": prox_compra,
                                                            "ejecutada": False,
                                                            "fecha_ejecucion" : 0
                                                            },
                                                "venta": {
                                                            "orderId": "",
                                                            "price": prox_venta,
                                                            "ejecutada": False,
                                                            "fecha_ejecucion" : 0
                                                }})
                    print("Grid Actual:")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print(json.dumps(parejas_compra_venta,indent=2))
                    print("")

    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_compra()")
        print(e)
        print("")
# -------------------------------------------

# Funció que coloca lsa ordenes de venta
# --------------------------------------
def ordenes_venta(exchange, symbol, grid):
    try:
        while True:
            
            # Colocar la orden de compra y actualiza la pareja de compra_veta
            actualizar_pareja(exchange=exchange, symbol=symbol)
            for compra_venta in parejas_compra_venta:
                if compra_venta["compra"]['ejecutada'] and not(compra_venta["venta"]['ejecutada']):
                    
                    # Obtener las ordenes abriertas
                    ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol)
                    orden_venta_puesta = False
                    
                    # Verificar si la orden de venta esta puesta
                    for orden in ordenes:
                        if (0.999*compra_venta['venta']['price'] <= float(orden['price']) <= 1.001*compra_venta['venta']['price']) and orden['reduceOnly']:
                            orden_venta_puesta = True
                    
                    if not(orden_venta_puesta):
                        # Consulta la orden compra para obtener la cantidad
                        ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=compra_venta['compra']['orderId'])
                        qty = ordenes[0]['qty']
                        
                        # Actualizar la pareja de nuevo para asegurar que la venta no este ejecutada
                        actualizar_pareja(exchange=exchange, symbol=symbol)
                        if compra_venta["compra"]['ejecutada'] and not(compra_venta["venta"]['ejecutada']):
                            
                            # Colocar la orden de venta
                            if precio_actual <= compra_venta["venta"]['price']:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["venta"]['price'], type="LIMIT",tpSize=qty)
                            else:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["venta"]['price'], type="MARKET",tpSize=qty)
                            
                            # Verificar que la respuesta sea válida antes de modificar la pareja
                            if orden != None:
                                actualizar_pareja(exchange=exchange, symbol=symbol)
                                compra_venta["venta"]['orderId'] = orden['orderId']
                                print("Grid Actual:")
                                print(grid)
                                print("Cantidad de grillas:", len(grid))
                                print(json.dumps(parejas_compra_venta,indent=2))
                                print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_venta()")
        print(e)
        print("")
# --------------------------------------

# Función que cierra todo en la estrategia
# ----------------------------------------
# ----------------------------------------


# Iniciar estrategia
iniciar_estrategia = False

# Consultar precio actual
precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
            
# Decimales del precio
decimales_precio = len(str(precio_actual).split(".")[-1])

# Decimales de la moneda
if precio_actual < 2:
    decimales_moneda = 0
if 2 < precio_actual < 100:
    decimales_moneda = 1
if 100 < precio_actual < 5000:
    decimales_moneda = 2
if precio_actual > 5000:
    decimales_moneda = 3

# Definir el multiplo
multiplo = 0
if 0.1 < precio_actual < 1:
    multiplo = 10
if 0.01 < precio_actual < 0.1:
    multiplo = 100
if precio_actual < 0.01:
    multiplo = 1000

# Inicializar las variables
grid = []
grid.append(precio_minimo)

# Iniciar Hilo que actualiza el grid
hilo_actualizar_grid = threading.Thread(target=actualizar_grid)
hilo_actualizar_grid.daemon = True
hilo_actualizar_grid.start()

# Cantidad de cada compra en USDT
cantidad_usdt = parametros()

# Iniciar estrategia
iniciar_estrategia = True

# Iniciar hilo del precio actual
hilo_precio_actual = threading.Thread(target=future_ws.precio_actual_activo, args=(exchange, activo))
hilo_precio_actual.daemon = True
hilo_precio_actual.start()

# Consultar precio actual
precio_actual = future_ws.precio_actual
while precio_actual == 0:
    precio_actual = future_ws.precio_actual

# Cantidad de la 1ra posicion a colocar
cantidad_monedas = round((cantidad_usdt/precio_actual), decimales_moneda)
if multiplo >= 10:
    cantidad_monedas = round(cantidad_monedas/multiplo)*multiplo

# Obtener el precio de la proxima compra y la proxima venta
prox_compra, prox_venta = prox_compra_venta(grid)

# Inicializar la lista de parejas
parejas_compra_venta = []
orden = future.nueva_orden(exchange=exchange, symbol=activo, order_type="LIMIT", quantity=cantidad_monedas, price=prox_compra, side="BUY", leverage=apalancamiento)
if orden != None:
    parejas_compra_venta.append({
                        "compra": {
                                    "orderId": orden['orderId'],
                                    "price": prox_compra,
                                    "ejecutada": False,
                                    "fecha_ejecucion" : 0
                                    },
                        "venta": {
                                    "orderId": "",
                                    "price": prox_venta,
                                    "ejecutada": False,
                                    "fecha_ejecucion" : 0
                        }})
    print(json.dumps(parejas_compra_venta,indent=2))
    print("")

# Iniciar Hilo de las ordenes compra
hilo_ordenes_compra = threading.Thread(target=ordenes_compra, args=(exchange,activo,cantidad_usdt,grid))
hilo_ordenes_compra.daemon = True
hilo_ordenes_compra.start()

# Iniciar Hilo de las ordenes venta
hilo_ordenes_venta = threading.Thread(target=ordenes_venta, args=(exchange,activo,grid))
hilo_ordenes_venta.daemon = True
hilo_ordenes_venta.start()

while True:

    # Verificar que el hilo del precio actual este activo
    if not(hilo_precio_actual.is_alive):
        hilo_precio_actual = threading.Thread(target=future_ws.precio_actual_activo, args=(exchange, activo))
        hilo_precio_actual.daemon = True
        hilo_precio_actual.start()

    # Verificar que el hilo actualizar grid este activo
    if not(hilo_actualizar_grid.is_alive()):
        hilo_actualizar_grid = threading.Thread(target=actualizar_grid, args=(ganancia_grid,))
        hilo_actualizar_grid.daemon = True
        hilo_actualizar_grid.start()
    
    # Verificar que el hilo de compras este activo
    if not(hilo_ordenes_compra.is_alive()):
        hilo_ordenes_compra = threading.Thread(target=ordenes_compra, args=(exchange,activo,cantidad_usdt,grid))
        hilo_ordenes_compra.daemon = True
        hilo_ordenes_compra.start()
    
    # Verificar que el hilo de venta este activo
    if not(hilo_ordenes_venta.is_alive()):
        hilo_ordenes_venta = threading.Thread(target=ordenes_venta, args=(exchange,activo,grid))
        hilo_ordenes_venta.daemon = True
        hilo_ordenes_venta.start()
