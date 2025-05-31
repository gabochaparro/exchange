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
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime


# Abrir el archivo parametros.json y cargar su contenido
parametros = json.load(open("future/estrategias/infinity/parametros.json", "r"))

# PARAMETROS DE LA ESTRATEGIA
# ---------------------------
exchange = parametros['exchange']                      # Exchange a utilizar
activo = parametros['activo']                          # Activo a operar
apalancamiento = parametros['apalancamiento']          # Se recomienda un apalancamiento muy bajo para esta estrategia (<=3x)
precio_minimo = parametros['precio_minimo']            # Por debajo del precio mínimo se mantiene la posición sin cambios
ganancia_grid = parametros['ganancia_grid']+0.11       # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
cuenta = future.margen_disponible(exchange=exchange)   # Inversión de la estrategia
tp = float(parametros['tp'])                           # Take profit para detener la estrategia por completo
sl = float(parametros['sl'])                           # Stop Loss para detener la estrategia por completo
tipo = "LONG"                                          # LONG o SHORT. Si se deja en blanco opera en ambas direcciones
# ---------------------------


# Función que actualiza el grid
# -----------------------------
def actualizar_grid():
    try:
        # variables globales
        global precio_actual

        while True:
            
            # Iniciar la estrategia
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
        print("Tipo:", tipo.upper())
        print("Inversión mínima:", inversion_minima, "USDT")
        print("Rango mínimo:", precio_minimo, "USDT")
        print("Rango máximo: INFINITO")
        print("Cantidad de grids:", len(grid))
        print("Cantidad de cada compra:", cantidad_usdt, "USDT")
        print(f"Ganancias por cada grid: {ganancia_grid-0.11}%")
        print("Inversión inicial:", round(cuenta*apalancamiento,2), "USDT")
        print("Cuenta:", round(cuenta,2), "USDT")
        print(f"Apalancamiento: {apalancamiento}x")
        print("")
        print("Precio actual:", precio_actual, "USDT")
        print("Proxima compra:", precio_compra, "USDT")
        print("Próxima venta:", precio_venta, "USDT")
        print("Primera compra:", cantidad_monedas, activo.upper(), f"({round(cantidad_monedas*precio_compra,2)} USDT)")
        print("-----------------------------------------")
        print("")

        # Detener estrategia por fondos insuficientes
        if cantidad_usdt <= 5 or cuenta*apalancamiento < inversion_minima:
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
                if grilla > prox_compra > grilla*(1-ganancia_grid/100):
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
        # Mantener el margen disponible
        margen()

        # LONG
        if tipo.upper() == "" or tipo.upper() == "LONG":
            for pareja in parejas_compra_venta:
                
                # BYBIT
                if exchange.upper() == "BYBIT":
                    # Obtener la orden de compra en BYBIT
                    ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['compra']['orderId'])
                    if ordenes != None:
                        if ordenes[0]['orderStatus'] == "Filled" and pareja['compra']['ejecutada'] == False:
                            pareja['compra']['ejecutada'] = True
                            pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            mostrar_lista(parejas_compra_venta)
                            print(json.dumps(parejas_compra_venta,indent=2))
                            print("")
                    
                    # Obtener la orden de venta en BYBIT
                    if pareja['venta']['orderId'] != "":
                        ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['venta']['orderId'])
                        if ordenes != None:
                            if ordenes[0]['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['general']['beneficios'] = cantidad_usdt*(ganancia_grid-0.11)/100
                                print("Grid Actual:")
                                print(grid)
                                print("Cantidad de grillas:", len(grid))
                                mostrar_lista(parejas_compra_venta)
                                print(json.dumps(parejas_compra_venta,indent=2))
                                print("")

                    # Limpiar la lista
                    ordenes = future.obtener_posicion(exchange, symbol)
                    if ordenes[0]['size'] == "0":
                        if pareja['compra']['ejecutada'] and not(pareja['venta']['ejecutada']):
                            print("Removiendo pareja...", pareja)
                            parejas_compra_venta.remove(pareja)
                            mostrar_lista(parejas_compra_venta)

                    if not(pareja['compra']['ejecutada']):
                        ordenes_abiertas = future.obtener_ordenes(exchange, symbol)
                        orden_puesta = False
                        for orden in ordenes_abiertas:
                            if 0.999*pareja['compra']['price'] <= float(orden['price']) <= 1.001*pareja['compra']['price']:
                                orden_puesta = True
                        if not(orden_puesta):
                            print("Removiendo pareja...", pareja)
                            parejas_compra_venta.remove(pareja)
                            mostrar_lista(parejas_compra_venta)
        
        # SHORT
        if tipo.upper() == "" or tipo.upper() == "SHORT":
            for pareja in parejas_compra_venta_short:
                # BYBIT
                if exchange.upper() == "BYBIT":
                    # Obtener la orden de compra en BYBIT
                    ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['compra']['orderId'])
                    if ordenes != None:
                        if ordenes[0]['orderStatus'] == "Filled" and pareja['compra']['ejecutada'] == False:
                            pareja['compra']['ejecutada'] = True
                            pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                            pareja['general']['beneficios'] = cantidad_usdt*(ganancia_grid-0.11)/100
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            mostrar_lista(parejas_compra_venta_short)
                            print(json.dumps(parejas_compra_venta_short,indent=2))
                            print("")
                    
                    # Obtener la orden de venta en BYBIT
                    if pareja['venta']['orderId'] != "":
                        ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['venta']['orderId'])
                        if ordenes != None:
                            if ordenes[0]['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                print("Grid Actual:")
                                print(grid)
                                print("Cantidad de grillas:", len(grid))
                                mostrar_lista(parejas_compra_venta_short)
                                print(json.dumps(parejas_compra_venta_short,indent=2))
                                print("")

                    # Limpiar la lista
                    ordenes = future.obtener_posicion(exchange, symbol)
                    if ordenes[1]['size'] == "0":
                        if pareja['compra']['ejecutada'] and not(pareja['venta']['ejecutada']):
                            print("Removiendo pareja...", pareja)
                            parejas_compra_venta_short.remove(pareja)
                            mostrar_lista(parejas_compra_venta_short)

                    if not(pareja['venta']['ejecutada']):
                        ordenes_abiertas = future.obtener_ordenes(exchange, symbol)
                        orden_puesta = False
                        for orden in ordenes_abiertas:
                            if 0.999*pareja['venta']['price'] <= float(orden['price']) <= 1.001*pareja['venta']['price']:
                                orden_puesta = True
                        if not(orden_puesta):
                            print("Removiendo pareja...", pareja)
                            parejas_compra_venta.remove(pareja)
                            mostrar_lista(parejas_compra_venta_short)
    
    except Exception as e:
        print("ERROR EN LA FUNCION actualizar_pareja()")
        print(e)
        print("")
# ----------------------------------------------------------------

# Función que coloca las ordenes de compra para LONG
# --------------------------------------------------
def ordenes_compra(exchange, symbol, cantidad_usdt, grid):
    try:
        while True:
            if tipo.upper() == "" or tipo.upper() == "LONG":
                
                # Consultar precio actual
                precio_actual = future_ws.precio_actual

                # Obtener el precio de la proxima compra y la proxima venta
                prox_compra, prox_venta = prox_compra_venta(grid)

                # Verificar si la pareja compra_venta esta activa
                actualizar_pareja(exchange=exchange, symbol=symbol)
                orden_compra_puesta = False
                for pareja in parejas_compra_venta:
                    if pareja["compra"]['price'] == prox_compra and not(pareja["venta"]['ejecutada']):
                        orden_compra_puesta = True
                
                # Cantidad de cada compra
                qty = round((cantidad_usdt/precio_actual),decimales_moneda)
                
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                # Colocar la orden de compra y crear la pareja de compra_veta
                if not(orden_compra_puesta):
                    if future.margen_disponible(exchange)*apalancamiento > cantidad_usdt:
                        orden = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_compra, side="BUY", leverage=apalancamiento)
                        if orden != None:
                            parejas_compra_venta.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": 0
                                                                    },
                                                        "compra": {
                                                                    "orderId": orden['orderId'],
                                                                    "price": prox_compra,
                                                                    "cantidad": qty,
                                                                    "monto": qty*prox_compra,
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": "",
                                                                    "price": prox_venta,
                                                                    "cantidad": qty,
                                                                    "monto": qty*prox_venta,
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                        }})
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            mostrar_lista(parejas_compra_venta)
                            print(json.dumps(parejas_compra_venta,indent=2))
                            print("")

    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_compra()")
        print(e)
        print("")
# --------------------------------------------------

# Funció que coloca lsa ordenes de venta para LONG
# ------------------------------------------------
def ordenes_venta(exchange, symbol, grid):
    try:
        while True:
            if tipo.upper() == "" or tipo.upper() == "LONG":
                
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
                                if precio_actual < compra_venta["venta"]['price']:
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
                                    mostrar_lista(parejas_compra_venta)
                                    print(json.dumps(parejas_compra_venta,indent=2))
                                    print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_venta()")
        print(e)
        print("")
# ------------------------------------------------

# Función que coloca las ordenes de venta para SHORT
# --------------------------------------------------
def ordenes_venta_short(exchange, symbol, cantidad_usdt, grid):
    try:
        while True:
            if tipo.upper() == "" or tipo.upper() == "SHORT":
                # Consultar precio actual
                precio_actual = future_ws.precio_actual

                # Obtener el precio de la proxima compra y la proxima venta
                prox_compra, prox_venta = prox_compra_venta(grid)

                # Verificar si la pareja compra_venta esta activa
                actualizar_pareja(exchange=exchange, symbol=symbol)
                orden_venta_puesta = False
                for pareja in parejas_compra_venta_short:
                    if pareja["venta"]['price'] == prox_venta and not(pareja["compra"]['ejecutada']):
                        
                        # Obtener las ordenes abiertas
                        ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['venta']['orderId'])
                        if ordenes[0]['orderStatus'] == "New":
                            orden_venta_puesta = True
                
                # Cantidad de cada compra
                qty = round((cantidad_usdt/precio_actual),decimales_moneda)
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                # Colocar la orden de compra y crear la pareja de compra_veta
                if not(orden_venta_puesta):
                    if future.margen_disponible(exchange)*apalancamiento > cantidad_usdt:
                        orden = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_venta, side="SELL", leverage=apalancamiento)
                        if orden != None:
                            parejas_compra_venta_short.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": 0
                                                                    },
                                                        "compra": {
                                                                    "orderId": "",
                                                                    "price": prox_compra,
                                                                    "cantidad": qty,
                                                                    "monto": qty*prox_compra,
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": orden['orderId'],
                                                                    "price": prox_venta,
                                                                    "cantidad": qty,
                                                                    "monto": qty*prox_venta,
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                        }})
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            mostrar_lista(parejas_compra_venta_short)
                            print(json.dumps(parejas_compra_venta_short,indent=2))
                            print("")

    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_compra()")
        print(e)
        print("")
# --------------------------------------------------

# Funció que coloca lsa ordenes de compra para SHORT
# --------------------------------------------------
def ordenes_compra_short(exchange, symbol, grid):
    try:
        while True:
            if tipo.upper() == "" or tipo.upper() == "SHORT":
                
                # Colocar la orden de compra y actualiza la pareja de compra_veta
                actualizar_pareja(exchange=exchange, symbol=symbol)
                for compra_venta in parejas_compra_venta_short:
                    if compra_venta["venta"]['ejecutada'] and not(compra_venta["compra"]['ejecutada']):
                        
                        # Obtener las ordenes abriertas
                        ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol)
                        orden_compra_puesta = False
                        
                        # Verificar si la orden de compra esta puesta
                        for orden in ordenes:
                            if (0.999*compra_venta['compra']['price'] <= float(orden['price']) <= 1.001*compra_venta['compra']['price']) and orden['reduceOnly']:
                                orden_compra_puesta = True
                        
                        if not(orden_compra_puesta):
                            # Consulta la orden venta para obtener la cantidad
                            ordenes = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=compra_venta['venta']['orderId'])
                            qty = ordenes[0]['qty']
                            
                            # Actualizar la pareja de nuevo para asegurar que la compra no esté ejecutada
                            actualizar_pareja(exchange=exchange, symbol=symbol)
                            if compra_venta["venta"]['ejecutada'] and not(compra_venta["compra"]['ejecutada']):
                                
                                # Colocar la orden de compra
                                if precio_actual > compra_venta["compra"]['price']:
                                    orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=compra_venta["compra"]['price'], type="LIMIT",tpSize=qty)
                                else:
                                    orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=compra_venta["compra"]['price'], type="MARKET",tpSize=qty)
                                
                                # Verificar que la respuesta sea válida antes de modificar la pareja
                                if orden != None:
                                    actualizar_pareja(exchange=exchange, symbol=symbol)
                                    compra_venta["compra"]['orderId'] = orden['orderId']
                                    print("Grid Actual:")
                                    print(grid)
                                    print("Cantidad de grillas:", len(grid))
                                    mostrar_lista(parejas_compra_venta_short)
                                    print(json.dumps(parejas_compra_venta_short,indent=2))
                                    print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_venta()")
        print(e)
        print("")
# --------------------------------------------------

# Función que mantiene la disponibilidad del margen
# -------------------------------------------------
def margen():
    try:
        # Verificar si no hay margen disponible para la compra
        if future.margen_disponible(exchange)*apalancamiento < cantidad_usdt:
            
            # LONG
            if tipo == "LONG":
                mas_bajo = future_ws.precio_actual
                pendiente = 0
                for pareja in parejas_compra_venta:
                    
                    # Buscar le mas bajo
                    if pareja['compra']['orderId'] != "" and not(pareja['compra']['ejecutada']) and pareja['compra']['price'] < mas_bajo:
                        mas_bajo = pareja['compra']['price']
                        pareja_eliminar = pareja
                    
                    # Contar las parejas pendiente
                    if not(pareja['compra']['ejecutada']):
                        pendiente = pendiente + 1
                
                # Cancelar la orden sólo si hay mas de una
                if  pendiente > 1:
                    
                    # Cancelar orden mas baja
                    future.cancelar_orden(exchange, activo, pareja_eliminar['compra']['orderId'])

                    # Remover la pareja mas baja
                    parejas_compra_venta.remove(pareja_eliminar)
            
            # SHORT
            if tipo == "SHORT":
                mas_alto = future_ws.precio_actual
                pendiente = 0
                for pareja in parejas_compra_venta:
                    if pareja['venta']['orderId'] != "" and not(pareja['venta']['ejecutada']) and pareja['venta']['price'] > mas_alto:
                        mas_alto = pareja['venta']['price']
                        pareja_eliminar = pareja
                    
                    # Contar las parejas pendiente
                    if not(pareja['compra']['ejecutada']):
                        pendiente = pendiente + 1
                
                # Cancelar la orden sólo si hay mas de una
                if  pendiente > 1:
                                    
                    # Cancelar orden mas baja
                    future.cancelar_orden(exchange, activo, pareja_eliminar['venta']['orderId'])

                    # Remover la pareja mas baja
                    parejas_compra_venta.remove(pareja_eliminar)
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN margen()")
        print(e)
        print("")
# -------------------------------------------------

# Función que muestra una imagen de la lista de parejas
# -----------------------------------------------------
def mostrar_lista(data):
    try:

        # Crear una imagen en blanco
        img_width, img_height = 300, 300*len(data)
        background_color = (35, 35, 40)
        text_color = (200, 200, 200)
        greenlight_color = (0, 255, 0)
        redlight_color = (255, 0, 0)
        image = Image.new('RGB', (img_width, img_height), color=background_color)

        # Configurar el objeto de dibujo y la fuente
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()  # Puedes cambiar esto por una fuente específica si lo deseas

        # Dibujar los datos en la imagen
        draw.text((10, 10), f" - INFINITY  Future - {activo.upper()} - {datetime.now().strftime('%Y-%m-%d - %I:%M:%S %p')} -", font=font, fill=text_color)
        draw.text((10, 30), f"Balance inicial:", font=font, fill=text_color)
        draw.text((180, 30), f"{round(balance_inicial,2)} USDT", font=font, fill=text_color)
        draw.text((10, 50), f"Balance actual:", font=font, fill=text_color)
        draw.text((180, 50), f"{round(future.patrimonio(exchange),2)} USDT", font=font, fill=text_color)
        
        ganancias_grid = 0
        for pareja in parejas_compra_venta:
            ganancias_grid = ganancias_grid + pareja['general']['beneficios']
        draw.text((10, 70), f"Ganancias del grid:", font=font, fill=text_color)
        draw.text((180, 70), f"{round(ganancias_grid,3)} USDT ({round(100*ganancias_grid/balance_inicial,2)}%)", font=font, fill=greenlight_color)

        ganancia = ganancia_actual()
        if ganancia >= 0:
            color_ganancias = greenlight_color
        else:
            color_ganancias = redlight_color
        draw.text((10, 90), f"Ganancia actual:", font=font, fill=text_color)
        draw.text((180, 90), f"{round(balance_inicial*ganancia/100,3)} USDT ({round(ganancia,2)}%)", font=font, fill=color_ganancias)
       
        y_text = 120
        for item in data:
            general = item['general']
            compra = item['compra']
            venta = item['venta']

            draw.text((10, y_text), f"----------------------------------------------------------------------------------------------", font=font, fill=text_color)
            y_text += 20
            draw.text((10, y_text), f"{general['fecha']}", font=font, fill=text_color)
            draw.text((180, y_text), f"+{round(general['beneficios'],3)}", font=font, fill=greenlight_color)
            y_text += 20
            draw.text((10, y_text), f"Compra Limit", font=font, fill=greenlight_color)
            draw.text((180, y_text), f"Venta Limit", font=font, fill=redlight_color)
            y_text += 20
            draw.text((10, y_text), f"Precio: {compra['price']} USDT", font=font, fill=text_color)
            draw.text((180, y_text), f"Precio: {venta['price']} USDT", font=font, fill=text_color)
            y_text += 20
            draw.text((10, y_text), f"Cantidad: {compra['cantidad']} {activo.upper()}", font=font, fill=text_color)
            draw.text((180, y_text), f"Cantidad: {venta['cantidad']} {activo.upper()}", font=font, fill=text_color)
            y_text += 20
            draw.text((10, y_text), f"Monto: {round(compra['monto'],3)} USDT", font=font, fill=text_color)
            draw.text((180, y_text), f"Monto: {round(venta['monto'],3)} USDT", font=font, fill=text_color)
            y_text += 20
            draw.text((10, y_text), f"{'Ejecutada' if compra['ejecutada'] else 'Pendiente'}", font=font, fill=text_color)
            draw.text((180, y_text), f"{'Ejecutada' if venta['ejecutada'] else 'Pendiente'}", font=font, fill=text_color)
            y_text += 20
            draw.text((10, y_text), f"{compra['fecha_ejecucion']}", font=font, fill=text_color)
            draw.text((180, y_text), f"{venta['fecha_ejecucion']}", font=font, fill=text_color)
            y_text += 30  # Espacio entre bloques de datos

        # Guardar la imagen
        image.save('future/estrategias/infinity/output.png')

        # Mostrar la imagen
        #image.show()

    except Exception as e:
        print("ERROR EN LA FUNCIÓN mostrar_lista()")
        print(e)
        print("")
# -----------------------------------------------------

# Función que mide la ganancia actual (en porcentaje %)
# -----------------------------------------------------
def ganancia_actual():
    try:
        return 100*(future.patrimonio(exchange) - balance_inicial)/balance_inicial
    
    except Exception  as e:
        print("ERROR EN LA FUNCIÓN ganancia_actual()")
        print(e)
        print("")
# -----------------------------------------------------

# Función que cierra todo
# -----------------------
def cerrar_todo():
    try:
        if tipo == "":
            print("CERRANDO ESTRTATEGIA...")
            future.cancelar_orden(exchange, activo, orderId="")
            future.cerrar_posicion(exchange, activo, "LONG")
            future.cerrar_posicion(exchange, activo, "SHORT")
        else:
            print("CERRANDO ESTRTATEGIA...")
            future.cancelar_orden(exchange, activo, orderId="")
            future.cerrar_posicion(exchange, activo, tipo)

    except Exception as e:
        print("ERROR CERRANDO TODO")
        print(e)
        print("")
# -----------------------

# Función que detiene la estrategia por TP/SL
#--------------------------------------------
def detener_estrategia():
    try:
        ganancias_grid = 0
        for pareja in parejas_compra_venta:
            ganancias_grid = ganancias_grid + pareja['general']['beneficios']

        if ganancia_actual() > 1.00369*tp and 100*ganancias_grid/balance_inicial > 1.00369*tp and tp > 0:
            iniciar_estrategia == False
            cerrar_todo()
            print("ESTRATEGIA DETENIDA POR TP!!!")
            print("")
            mostrar_lista(parejas_compra_venta)
            exit()
            
        if ganancia_actual() <= (-1)*(sl) and sl > 0:
            iniciar_estrategia == False
            cerrar_todo()
            print("ESTRATEGIA DETENIDA POR SL!!!")
            print("")
            mostrar_lista(parejas_compra_venta)
            exit()
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN detener_estrategia()")
        print(e)
        print("")
#--------------------------------------------


# Balance inicial
balance_inicial = future.patrimonio(exchange)

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
if 0.1 < precio_actual < 0.5:
    multiplo = 1
if 0.05 < precio_actual < 0.1:
    multiplo = 10
if 0.01 < precio_actual < 0.05:
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
parejas_compra_venta_short = []
if tipo.upper() == "" or tipo.upper() == "LONG":
    orden = future.nueva_orden(exchange=exchange, symbol=activo, order_type="LIMIT", quantity=cantidad_monedas, price=prox_compra, side="BUY", leverage=apalancamiento)
    if orden != None:
        parejas_compra_venta.insert(0,{
                            "general": {
                                        "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                        "beneficios": 0
                                        },
                            "compra": {
                                        "orderId": orden['orderId'],
                                        "price": prox_compra,
                                        "cantidad": cantidad_monedas,
                                        "monto": cantidad_monedas*prox_compra,
                                        "ejecutada": False,
                                        "fecha_ejecucion" : "-"
                                        },
                            "venta": {
                                        "orderId": "",
                                        "price": prox_venta,
                                        "cantidad": cantidad_monedas,
                                        "monto": cantidad_monedas*prox_venta,
                                        "ejecutada": False,
                                        "fecha_ejecucion" : "-"
                            }})
        mostrar_lista(parejas_compra_venta)
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
if tipo.upper() == "" or tipo.upper() == "SHORT":
    orden = future.nueva_orden(exchange=exchange, symbol=activo, order_type="LIMIT", quantity=cantidad_monedas, price=prox_venta, side="SELL", leverage=apalancamiento)
    if orden != None:
        parejas_compra_venta_short.insert(0,{
                            "general": {
                                        "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                        "beneficios": 0
                                        },
                            "compra": {
                                        "orderId": "",
                                        "price": prox_compra,
                                        "cantidad": cantidad_monedas,
                                        "monto": cantidad_monedas*prox_compra,
                                        "ejecutada": False,
                                        "fecha_ejecucion" : "-"
                                        },
                            "venta": {
                                        "orderId": orden['orderId'],
                                        "price": prox_venta,
                                        "cantidad": cantidad_monedas,
                                        "monto": cantidad_monedas*prox_venta,
                                        "ejecutada": False,
                                        "fecha_ejecucion" : "-"
                            }})
        print(json.dumps(parejas_compra_venta_short,indent=2))
        print("")

    # Iniciar Hilo de las ordenes compra
    hilo_ordenes_venta_short = threading.Thread(target=ordenes_venta_short, args=(exchange,activo,cantidad_usdt,grid))
    hilo_ordenes_venta_short.daemon = True
    hilo_ordenes_venta_short.start()

    # Iniciar Hilo de las ordenes venta
    hilo_ordenes_compra_short = threading.Thread(target=ordenes_compra_short, args=(exchange,activo,grid))
    hilo_ordenes_compra_short.daemon = True
    hilo_ordenes_compra_short.start()

while iniciar_estrategia:

    # Detener la estrategia por TP/SL
    detener_estrategia()

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
    
    if tipo.upper() == "" or tipo.upper() == "LONG":
        
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
    
    if tipo.upper() == "" or tipo.upper() == "SHORT":
        
        # Verificar que el hilo de compras este activo
        if not(hilo_ordenes_venta_short.is_alive()):
            hilo_ordenes_venta_short = threading.Thread(target=ordenes_venta_short, args=(exchange,activo,cantidad_usdt,grid))
            hilo_ordenes_venta_short.daemon = True
            hilo_ordenes_venta_short.start()
        
        # Verificar que el hilo de venta este activo
        if not(hilo_ordenes_compra_short.is_alive()):
            hilo_ordenes_compra_short = threading.Thread(target=ordenes_compra_short, args=(exchange,activo,grid))
            hilo_ordenes_compra_short.daemon = True
            hilo_ordenes_compra_short.start()
