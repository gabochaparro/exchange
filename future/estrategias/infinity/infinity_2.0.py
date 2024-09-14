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



# PARAMETROS DE LA ESTRATEGIA
# ---------------------------
# Abrir el archivo parametros.json y cargar su contenido
parametros = json.load(open("future/estrategias/infinity/parametros_infinity_2.0.json", "r"))

exchange = parametros['exchange']                                                                   # Exchange a utilizar
activo = parametros['activo']                                                                       # Activo a operar
apalancamiento = parametros['apalancamiento']                                                       # Se recomienda un apalancamiento muy bajo para esta estrategia (<=3x)
precio_referencia = parametros['precio_referencia']                                                 # Precio de referencia
ganancia_grid = parametros['distancia_grid']+0.207                                                  # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
cuenta = future.patrimonio(exchange=exchange)                                                       # Inversión de la estrategia
tp = float(parametros['tp'])                                                                        # Take profit para detener la estrategia por completo
sl = float(parametros['sl'])                                                                        # Stop Loss para detener la estrategia por completo
tipo = parametros['direccion'].upper()                                                              # LONG o SHORT. Si se deja en blanco opera en ambas direcciones
ganancia_grid_long = parametros['ganancia_grid_long']                                               # Ganancias por cada grid long
ganancia_grid_short = parametros['ganancia_grid_short']                                             # Ganancias por cada grid short
cantidad_usdt = cuenta*ganancia_grid_long/parametros['distancia_grid']                              # Importe en USDT para cada compra del long
cantidad_usdt_short = cuenta*ganancia_grid_short/parametros['distancia_grid']                       # Importe en USDT para cada compra del short
condicional_long = parametros['condicional_long']
condicional_short = parametros['condicional_short']
# ---------------------------


# Función que actualiza el grid
# -----------------------------
def actualizar_grid():
    try:
        # variables globales y locales
        global precio_actual, grid
        referencia_nuevo_grid = precio_referencia

        while precio_actual != 0:
            #print(grid)
            
            # Iniciar la estrategia
            if iniciar_estrategia == True:
                
                # Consultar precio actual
                precio_actual = future_ws.precio_actual

            # LONG
            while grid[-1] <= precio_actual:
                
                # Agregar un nuevo nivel al grid
                nuevo_nivel = round(grid[-1]*(1+ganancia_grid/100),decimales_precio)
                if nuevo_nivel not in grid:
                    grid.append(nuevo_nivel)
                
                # Consultar precio actual
                if iniciar_estrategia == True:
                    precio_actual = future_ws.precio_actual
                else:
                    precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
                
                # Grilla actualizada
                if grid[-1] > precio_actual and iniciar_estrategia == True:
                    print("")
                    print("Grilla Actualizada.")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")

            # SHORT
            while grid[0] >= precio_actual:
                
                # Agregar un nuevo nivel al grid
                nuevo_nivel = round(grid[0]/(1+ganancia_grid/100),decimales_precio)
                if nuevo_nivel not in grid:
                    grid.insert(0,nuevo_nivel)
                
                # Consultar precio actual
                if iniciar_estrategia == True:
                    precio_actual = future_ws.precio_actual
                
                # Grilla actualizada
                if grid[0] < precio_actual and iniciar_estrategia == True:
                    print("")
                    print("Grilla Actualizada.")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")
            
            time.sleep(0.36)

            # Modificar el grid
            if precio_referencia != referencia_nuevo_grid:
                referencia_nuevo_grid = precio_referencia
                grid = []
                grid.append(precio_referencia)
    
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
        global apalancamiento, multiplo, cantidad_usdt, cantidad_usdt_short

        # Obtener el grid
        print("")
        print("Obteniendo grid...")
        print(grid)
        print("")
        
        # Obtener el precio de la proxima compra y la proxima venta
        print("")
        print("Buscando próximos niveles...")
        precio_compra, precio_venta = prox_compra_venta()
        print("Niveles encontrados.", precio_compra, precio_venta)

        # Revisar el apalancamiento
        if apalancamiento > future.apalancamiento_max(exchange=exchange,symbol=activo):
            apalancamiento = future.apalancamiento_max(exchange=exchange,symbol=activo)

        # Cantidad de la 1ra posicion a colocar
        cantidad_monedas = round((cantidad_usdt/precio_actual), decimales_moneda)
        if multiplo >= 1:
            cantidad_monedas = round(cantidad_monedas/multiplo)*multiplo
        cantidad_monedas_short = round((cantidad_usdt_short/precio_actual), decimales_moneda)
        if multiplo >= 1:
            cantidad_monedas_short = round(cantidad_monedas_short/multiplo)*multiplo
        
        # Imprimir Parametros
        print("")
        print("-----------------------------------------")
        print("Exchange:", exchange.upper())
        print( "Activo:", activo.upper())
        if tipo == "":
            print("Dirección:", "LONG-SHORT")
        else:
            print("Dirección:", tipo.upper())
        print("Precio de referencia:", precio_referencia, "USDT")
        print("Cantidad de cada compra long:", round(cantidad_usdt,2), "USDT")
        print("Cantidad de cada compra short:", round(cantidad_usdt_short,2), "USDT")
        print(f"Distancia entre cada grid: {ganancia_grid-0.11}%")
        print(f"Ganancas del grid long: {ganancia_grid_long}%")
        print(f"Ganancas del grid short: {ganancia_grid_short}%")
        print("Cuenta:", round(cuenta,2), "USDT")
        print(f"Apalancamiento: {apalancamiento}x")
        print("Inversión inicial:", round(cuenta*apalancamiento,2), "USDT")
        print("-----------------------------------------")
        print("Precio actual:", precio_actual, "USDT")
        print("Proxima compra:", precio_compra, "USDT")
        print("Próxima venta:", precio_venta, "USDT")
        print("Primera compra:", cantidad_monedas, activo.upper(), f"({round(cantidad_monedas*precio_compra,2)} USDT)")
        print("Primera venta:", cantidad_monedas_short, activo.upper(), f"({round(cantidad_monedas_short*precio_venta,2)} USDT)")
        print("-----------------------------------------")
        print("")
        
        # Pedir confirmación para iniciar estrategia
        iniciar_estrategia = "*"
        while iniciar_estrategia != "":
            iniciar_estrategia = input("Presiona ENTER para iniciar la estrategia")
        if iniciar_estrategia == "":
            return cantidad_usdt, cantidad_usdt_short
        
    except Exception as e:
        print("ERROR EN LA FUNCIÓN parametros()")
        print(e)
        print("")
        exit()
# -----------------------------------------

# FUnción que se encarga de entrar la próxima compra y la próxima venta
# ---------------------------------------------------------------------
def prox_compra_venta():
    try:
        # Variables globales
        global precio_actual, grid

        # Cosultar el precio actual
        if iniciar_estrategia == True:
            precio_actual = future_ws.precio_actual
        else:
            precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
        
        # Recorrer el grid y encontrar el próximo precio de compra y venta
        prox_compra = 0
        prox_venta = 0
        while prox_compra == 0 or prox_venta == 0:
            for grilla in grid:
                if grilla < precio_actual < grilla*(1+ganancia_grid/100):
                    prox_compra = grilla
                    prox_venta = grid[grid.index(grilla)+1]
            
                # Cosultar el precio actual
                if iniciar_estrategia == True:
                    precio_actual = future_ws.precio_actual
                else:
                    precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)

        #print(prox_compra, prox_venta)
        return prox_compra, prox_venta
    
    except Exception as e:
        print("ERROR EN prox_compra_venta()")
        print(e)
        print("")
# ---------------------------------------------------------------------

# Función que actualiza el estado de las parejas de compra y venta long
# ---------------------------------------------------------------------
def actualizar_pareja_long(exchange, symbol):
    try:

        ti = time.time()

        if tipo.upper() == "" or tipo.upper() == "LONG":

            #Obtener historial de ordenes
            historial_ordenes = future.obtener_historial_ordenes(exchange=exchange, symbol=symbol)
            
            for pareja in parejas_compra_venta:
                for orden in historial_ordenes:
                    
                    # Obtener la orden de compra
                    if orden['orderId'] == pareja['compra']['orderId']:
                
                        # BYBIT
                        if exchange.upper() == "BYBIT":

                            # Obtener la orden de compra en Bybit
                            if orden['orderStatus'] == "Filled" and pareja['compra']['ejecutada'] == False:
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                mostrar_lista(parejas_compra_venta)
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                print("")
                    
                    # Obtener la orden de venta
                    if orden['orderId'] == pareja['venta']['orderId']:
                        
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                    
                            # Obtener la orden de venta en Bybit
                            if orden['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['general']['beneficios'] = 0.9989*(float(orden['qty'])*float(orden['price'])-pareja['compra']['monto'])
                                mostrar_lista(parejas_compra_venta)
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                print("")
                                
                                # Cancelar la orden de SL en caso tenga
                                if pareja['sl']['orderId'] != "":
                                    future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                    print("SL Cancelado.")
                            
                            # Obtener la orden de sl
                            if pareja['sl']['orderId'] != "":
                                ordenes_sl = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['sl']['orderId'])
                                
                                if ordenes_sl != None and ordenes_sl != []:                         
                                    if ordenes_sl[0]['orderStatus'] == "Filled" and ordenes_venta[0]['orderStatus'] == "Untriggered":
                                        
                                        # Cancelar la orden venta en caso se haya tocado el SL
                                        if pareja['venta']['orderId'] != "":
                                            future.cancelar_orden(exchange, activo, orderId=pareja['venta']['orderId'])
                                            print("TP Cancelado.")
                                            print("")
                                            parejas_compra_venta.remove(pareja)
                                            mostrar_lista(parejas_compra_venta)
                                            print("Pareja removida.", pareja)
                                            print("")

        #print("Parejas long actualizadas", time.time()-ti, "segundos")
    
    except Exception as e:
        print("ERROR EN LA FUNCION actualizar_pareja_long()")
        print(e)
        print("")
# ---------------------------------------------------------------------

# Función que actualiza el estado de las parejas de compra y venta short
# ----------------------------------------------------------------------
def actualizar_pareja_short(exchange, symbol):
    try:

        ti = time.time()

        if tipo.upper() == "" or tipo.upper() == "SHORT":

            #Obtener historial de ordenes
            historial_ordenes = future.obtener_historial_ordenes(exchange=exchange, symbol=symbol)
            
            for pareja in parejas_compra_venta_short:
                for orden in historial_ordenes:

                    # Obtener la orden de compra
                    if orden['orderId'] == pareja['compra']['orderId']:
                
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                            
                            # Obtener la orden de compra en BYBIT
                                if orden['orderStatus'] == "Filled" and pareja['compra']['ejecutada'] == False:
                                    pareja['compra']['ejecutada'] = True
                                    pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                    pareja['general']['beneficios'] = 0.9989*(pareja['venta']['monto']-float(orden['qty'])*float(orden['price']))
                                    mostrar_lista(parejas_compra_venta_short)
                                    #print(json.dumps(parejas_compra_venta_short,indent=2))
                                    print("")
                                        
                                    # Cancelar la orden de SL en caso tenga
                                    if pareja['sl']['orderId'] != "":
                                        future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")

                    # Obtener la orden de Venta
                    if orden['orderId'] == pareja['venta']['orderId']:
                
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                            
                            # Obtener la orden de venta en BYBIT
                            if orden['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                print("Grid Actual:")
                                print(grid)
                                print("Cantidad de grillas:", len(grid))
                                mostrar_lista(parejas_compra_venta_short)
                                #print(json.dumps(parejas_compra_venta_short,indent=2))
                                print("")
                            
                            # Obtener la orden de sl en BYBIT
                            if pareja['sl']['orderId'] != "":
                                ordenes_sl = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['sl']['orderId'])
                                
                                if ordenes_sl != None and ordenes_sl != []:
                                    if ordenes_sl[0]['orderStatus'] == "Filled" and ordenes_compra[0]['orderStatus'] == "Untriggered":
                                        
                                        # Cancelar la orden compra en caso se haya tocado el SL
                                        if pareja['compra']['orderId'] != "":
                                            future.cancelar_orden(exchange, activo, orderId=pareja['compra']['orderId'])
                                            print("TP Cancelado.")
                                            print("")
                                            parejas_compra_venta.remove(pareja)
                                            mostrar_lista(parejas_compra_venta)
                                            print("Pareja removida.", pareja)
                                            print("")
    
        #print("Parejas short actualizadas", time.time()-ti, "segundos")
    
    except Exception as e:
        print("ERROR EN LA FUNCION actualizar_pareja_short()")
        print(e)
        print("")
# ----------------------------------------------------------------------

# Función que limpia las listas de las parejas
# --------------------------------------------
def limpiar_listas():
    try:

        # Variables globales
        global parejas_compra_venta, parejas_compra_venta_short
        
        while iniciar_estrategia:
            if parejas_compra_venta != [] or parejas_compra_venta_short != []:

                ti = time.time()

                # LONG
                if tipo.upper() == "" or tipo.upper() == "LONG":
                    for pareja in parejas_compra_venta:

                            # Limpiar la lista
                            posiciones = future.obtener_posicion(exchange, activo)
                            for posicion in posiciones:
                                
                                if posicion['positionIdx'] == 1:
                                    if posicion['size'] == "0":
                                        
                                        actualizar_pareja_long(exchange=exchange, symbol=activo)
                                        if pareja['compra']['ejecutada'] and not(pareja['venta']['ejecutada']):
                                            print("Removiendo pareja long...", pareja)
                                            print("")
                                            
                                            if pareja in parejas_compra_venta:
                                                parejas_compra_venta.remove(pareja)
                                                mostrar_lista(parejas_compra_venta)
                                        
                            
                            ordenes_abiertas = future.obtener_ordenes(exchange, activo)
                            actualizar_pareja_long(exchange=exchange, symbol=activo)
                            if not(pareja['compra']['ejecutada']):
                                orden_puesta = False
                                
                                if ordenes_abiertas != []:
                                    
                                    # Verificar si hay una orden limite
                                    for orden in ordenes_abiertas:
                                        if 0.999*pareja['compra']['price'] <= float(orden['price']) <= 1.001*pareja['compra']['price'] and orden['positionIdx'] == 1 and orden['side'] == "Buy":
                                            orden_puesta = True
                                        
                                        # Verificar si hay una orden condicional
                                        if orden['triggerPrice'] != "":
                                            if 0.999*pareja['compra']['price'] <= float(orden['triggerPrice']) <= 1.001*pareja['compra']['price'] and orden['positionIdx'] == 1 and orden['side'] == "Buy":
                                                orden_puesta = True
                                    
                                    if not(orden_puesta):
                                        print("Removiendo pareja short...", pareja)
                                        print("")
                                        
                                        if pareja in parejas_compra_venta:
                                            parejas_compra_venta.remove(pareja)
                                            mostrar_lista(parejas_compra_venta)
                
                # SHORT
                if tipo.upper() == "" or tipo.upper() == "SHORT":
                    for pareja in parejas_compra_venta_short:

                            # Limpiar la lista
                            posiciones = future.obtener_posicion(exchange, activo)
                            for posicion in posiciones:
                                
                                if posicion['positionIdx'] == 2:
                                    if posicion['size'] == "0":
                                        
                                        # Actualizar las parejas
                                        actualizar_pareja_short(exchange=exchange, symbol=activo)
                                        if pareja['venta']['ejecutada'] and not(pareja['compra']['ejecutada']):
                                            print("Removiendo pareja short...", pareja)
                                            
                                            if pareja in parejas_compra_venta_short:
                                                parejas_compra_venta_short.remove(pareja)
                                                mostrar_lista(parejas_compra_venta_short)

                                        
                            ordenes_abiertas = future.obtener_ordenes(exchange, activo)
                            actualizar_pareja_short(exchange=exchange, symbol=activo)
                            if not(pareja['venta']['ejecutada']):
                                orden_puesta = False
                                
                                if ordenes_abiertas != []:
                                    
                                    # Verificar si hay una orden limite
                                    for orden in ordenes_abiertas:
                                        if 0.999*pareja['venta']['price'] <= float(orden['price']) <= 1.001*pareja['venta']['price'] and orden['positionIdx'] == 2 and orden['side'] == "Sell":
                                            orden_puesta = True
                                        
                                        # Verificar si hay una orden condicional
                                        if orden['triggerPrice'] != "":
                                            if 0.999*pareja['venta']['price'] <= float(orden['triggerPrice']) <= 1.001*pareja['venta']['price'] and orden['positionIdx'] == 2 and orden['side'] == "Sell":
                                                orden_puesta = True
                                    
                                    if not(orden_puesta):
                                        print("Removiendo pareja short...", pareja)
                                        
                                        if pareja in parejas_compra_venta_short:
                                            parejas_compra_venta_short.remove(pareja)
                                            mostrar_lista(parejas_compra_venta_short)
            
                if time.time()-ti > 60:
                    print("Listas limpias", round(time.time()-ti, 2), "segundos")
                    print("")

    except Exception as e:
        print("ERROR EN LA FUNCIÓN limpiar_lista()")
        print(e)
        print("")
# --------------------------------------------

# Función que coloca las ordenes de compra para LONG
# --------------------------------------------------
def ordenes_compra(exchange, symbol):
    try:
        nueva_compra = 0
        nueva_venta = 0
        while iniciar_estrategia:
            if tipo.upper() == "" or tipo.upper() == "LONG":
                
                # Consultar precio actual
                precio_actual = future_ws.precio_actual

                # Obtener el precio de la proxima compra y la proxima venta
                prox_compra, prox_venta = prox_compra_venta()
                if nueva_compra != prox_compra or nueva_venta != prox_venta:
                    nueva_compra = prox_compra
                    nueva_venta = prox_venta
                    print(f"Próxima compra-venta: ({nueva_compra},{nueva_venta})")
                    print("")

                # Verificar si la pareja compra_venta esta activa
                orden_compra_puesta = False
                orden_condicional_compra_puesta = False
                orddenes_abiertas = future.obtener_ordenes(exchange=exchange, symbol=symbol)
                actualizar_pareja_long(exchange=exchange, symbol=symbol)
                for pareja in parejas_compra_venta:
                    for orden in orddenes_abiertas:
                        if not(pareja["venta"]['ejecutada']):

                            # Verificar la orden limite
                            if pareja["compra"]['ejecutada'] or (0.999*pareja["compra"]['price'] < float(orden['price']) < 1.001*pareja["compra"]['price'] and orden['positionIdx'] == 1 and orden['side'] == "Buy"):
                                if pareja["compra"]['price'] == prox_compra:
                                    orden_compra_puesta = True
                                
                            # Verificar la orden condicional
                            if orden['triggerPrice'] != "":
                                if pareja["compra"]['ejecutada'] or (0.999*pareja["compra"]['price'] < float(orden['triggerPrice']) < 1.001*pareja["compra"]['price'] and orden['positionIdx'] == 1 and orden['side'] == "Buy"):
                                    if pareja["compra"]['price'] == prox_venta:
                                        orden_condicional_compra_puesta = True
                
                # Cantidad de cada compra
                qty = round((cantidad_usdt/precio_actual),decimales_moneda)
                
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                orden_compra = None
                
                # Colocar la orden limite de compra y crear la pareja de compra_veta
                if not(orden_compra_puesta):
                    if future.margen_disponible(exchange)*apalancamiento > cantidad_usdt and precio_actual > prox_compra:
                        orden_compra = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_compra, side="BUY", leverage=apalancamiento)
                        if orden_compra != None:
                            parejas_compra_venta.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": 0
                                                                    },
                                                        "compra": {
                                                                    "orderId": orden_compra['orderId'],
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
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                
                # Colocar la orden condicional de compra y crear la pareja de compra_veta
                if not(orden_condicional_compra_puesta) and condicional_long:
                    if future.margen_disponible(exchange)*apalancamiento > cantidad_usdt and precio_actual < prox_venta:
                        orden_compra = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_venta, side="BUY", leverage=apalancamiento)
                        if orden_compra != None:
                            parejas_compra_venta.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": 0
                                                                    },
                                                        "compra": {
                                                                    "orderId": orden_compra['orderId'],
                                                                    "price": prox_venta,
                                                                    "cantidad": qty,
                                                                    "monto": qty*prox_venta,
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": "",
                                                                    "price": round(prox_venta*(1+ganancia_grid/100),decimales_precio),
                                                                    "cantidad": qty,
                                                                    "monto": qty*round(prox_venta*(1+ganancia_grid/100),decimales_precio),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                
                # Imprimir cambios
                if orden_compra != None:
                    print("Grid Actual:")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")
                    mostrar_lista(parejas_compra_venta)
                    #print(json.dumps(parejas_compra_venta,indent=2))
    
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_compra()")
        print(e)
        print("")
# --------------------------------------------------

# Funció que coloca lsa ordenes de venta para LONG
# ------------------------------------------------
def ordenes_venta(exchange, symbol):
    try:
        while iniciar_estrategia:
            
            if tipo.upper() == "" or tipo.upper() == "LONG":
                
                # Colocar la orden de compra
                for compra_venta in parejas_compra_venta:
                    if compra_venta["compra"]['ejecutada'] and compra_venta["venta"]['orderId'] == "":
                            
                        # Colocar la orden de venta
                        posiciones = future.obtener_posicion(exchange, activo)
                        
                        # Obtener el tamaño y el precio de la posición
                        size = "0"
                        for posicion in posiciones:
                            if posicion['positionIdx'] == 1:
                                size = posicion['size']
                                avgPrice = float(posicion['avgPrice'])
                        
                        if size != "0":
                            
                            # Colocar SL
                            '''
                            if ganancia_actual() < -3*parametros['ganancia_grid_long'] and precio_actual > 1.0001*compra_venta["compra"]['price']/(1+ganancia_grid/100):
                                if qty != "":
                                    orden_sl = future.stop_loss(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["compra"]['price']/(1+ganancia_grid/100),slSize=qty)
                                
                                # Verificar que la respuesta sea válida antes de modificar la pareja
                                if orden_sl != None:
                                    compra_venta["sl"]['orderId'] = orden_sl['orderId']
                                    print(json.dumps(parejas_compra_venta,indent=2))
                                    print("")
                                    '''
                            
                            # Colocar TP
                            orden = None
                            if precio_actual < compra_venta["venta"]['price'] > 1.0011*avgPrice:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["venta"]['price'], type="LIMIT",tpSize=str(compra_venta["venta"]['cantidad']))
                            if precio_actual > compra_venta["venta"]['price'] > 1.0011*avgPrice:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["venta"]['price'], type="MARKET",tpSize=str(compra_venta["venta"]['cantidad']))
                                
                            # Verificar que la respuesta sea válida antes de modificar la pareja
                            if orden != None:
                                compra_venta["venta"]['orderId'] = orden['orderId']
                                print("Grid Actual:")
                                print(grid)
                                print("Cantidad de grillas:", len(grid))
                                print("")
                                mostrar_lista(parejas_compra_venta)
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_venta()")
        print(e)
        print("")
# ------------------------------------------------

# Función que coloca las ordenes de venta para SHORT
# --------------------------------------------------
def ordenes_venta_short(exchange, symbol):
    try:
        nueva_compra = 0
        nueva_venta = 0
        while iniciar_estrategia:
            if tipo.upper() == "" or tipo.upper() == "SHORT":
                # Consultar precio actual
                precio_actual = future_ws.precio_actual

                # Obtener el precio de la proxima compra y la proxima venta
                prox_compra, prox_venta = prox_compra_venta()
                if nueva_compra != prox_compra or nueva_venta != prox_venta:
                    nueva_compra = prox_compra
                    nueva_venta = prox_venta
                    print(f"Próxima compra-venta: ({nueva_compra},{nueva_venta})")
                    print("")

                # Verificar si la pareja compra_venta esta activa
                orden_venta_puesta = False
                orden_condicional_venta_puesta = False
                orddenes_abiertas = future.obtener_ordenes(exchange=exchange, symbol=symbol)
                actualizar_pareja_short(exchange=exchange, symbol=symbol)
                for pareja in parejas_compra_venta_short:
                    for orden in orddenes_abiertas:
                        if not(pareja["compra"]['ejecutada']):
                        
                            # Verificar orden limite
                            if pareja["venta"]['ejecutada'] or (0.999*pareja["venta"]['price'] < float(orden['price']) < 1.001*pareja["venta"]['price'] and orden['positionIdx'] == 2 and orden['side'] == "Sell"):
                                if pareja["venta"]['price'] == prox_venta:
                                    orden_venta_puesta = True
                                
                            # Verificar orden condicional
                            if orden['triggerPrice'] != "":
                                if pareja["venta"]['ejecutada'] or (0.999*pareja["venta"]['price'] < float(orden['triggerPrice']) < 1.001*pareja["venta"]['price'] and orden['positionIdx'] == 2 and orden['side'] == "Sell"):
                                    if pareja["venta"]['price'] == prox_compra:
                                        orden_condicional_venta_puesta = True
                
                # Cantidad de cada compra
                qty = round((cantidad_usdt_short/precio_actual),decimales_moneda)
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                orden_venta = None
                
                # Colocar la orden limite de compra y crear la pareja de compra_veta
                if not(orden_venta_puesta):
                    if future.margen_disponible(exchange)*apalancamiento > cantidad_usdt_short and precio_actual < prox_venta:
                        orden_venta = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_venta, side="SELL", leverage=apalancamiento)
                        if orden_venta != None:
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
                                                                    "orderId": orden_venta['orderId'],
                                                                    "price": prox_venta,
                                                                    "cantidad": qty,
                                                                    "monto": qty*prox_venta,
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                
                # Colocar la orden condicional de compra y crear la pareja de compra_veta
                if not(orden_condicional_venta_puesta) and condicional_short:
                    if future.margen_disponible(exchange)*apalancamiento > cantidad_usdt_short and precio_actual > prox_compra:
                        orden_venta = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_compra, side="SELL", leverage=apalancamiento)
                        if orden_venta != None:
                            parejas_compra_venta_short.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": 0
                                                                    },
                                                        "compra": {
                                                                    "orderId": "",
                                                                    "price": round(prox_compra/(1+ganancia_grid/100),decimales_precio),
                                                                    "cantidad": qty,
                                                                    "monto": qty*round(prox_compra/(1+ganancia_grid/100),decimales_precio),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": orden_venta['orderId'],
                                                                    "price": prox_compra,
                                                                    "cantidad": qty,
                                                                    "monto": qty*prox_compra,
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                
                # Imprimir cambios
                if orden_venta != None:
                    print("Grid Actual:")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")
                    mostrar_lista(parejas_compra_venta_short)
                    #print(json.dumps(parejas_compra_venta_short,indent=2))
                    print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_compra()")
        print(e)
        print("")
# --------------------------------------------------

# Funció que coloca lsa ordenes de compra para SHORT
# --------------------------------------------------
def ordenes_compra_short(exchange, symbol):
    try:
        while iniciar_estrategia:

            if tipo.upper() == "" or tipo.upper() == "SHORT":
                
                # Colocar la orden de compra y actualiza la pareja de compra_veta
                for compra_venta in parejas_compra_venta_short:
                    if compra_venta["venta"]['ejecutada'] and compra_venta["compra"]['orderId'] == "":
                                
                        # Obtener posiciones
                        posiciones = future.obtener_posicion(exchange, activo)
                        
                        # Obtener el tamaño y el precio de la posición
                        size = "0"
                        for posicion in posiciones:
                            if posicion['positionIdx'] == 2:
                                size = posicion['size']
                                avgPrice = float(posicion['avgPrice'])
                        
                        # Colocar el SL y el TP solo si existe una posición
                        if size != "0":
                                
                            # Colocar SL
                            '''
                            if ganancia_actual() < -3*parametros['ganancia_grid_short'] and precio_actual < 0.999*compra_venta["venta"]['price']*(1+ganancia_grid/100):
                                if qty != "":
                                    orden_sl = future.stop_loss(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=compra_venta["venta"]['price']*(1+ganancia_grid/100),slSize=qty)
                                
                                # Verificar que la respuesta sea válida antes de modificar la pareja
                                if orden_sl != None:
                                    compra_venta["sl"]['orderId'] = orden_sl['orderId']
                                    print(json.dumps(parejas_compra_venta_short,indent=2))
                                    print("")
                                    '''
                            
                            # Colocar TP
                            if precio_actual > compra_venta["compra"]['price'] < 0.999*avgPrice:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=compra_venta["compra"]['price'], type="LIMIT",tpSize=str(compra_venta["compra"]['cantidad']))
                                
                                # Verificar que la respuesta sea válida antes de modificar la pareja
                                if orden != None:
                                    compra_venta["compra"]['orderId'] = orden['orderId']
                                    print("Grid Actual:")
                                    print(grid)
                                    print("Cantidad de grillas:", len(grid))
                                    print("")
                                    mostrar_lista(parejas_compra_venta_short)
                                    #print(json.dumps(parejas_compra_venta_short,indent=2))
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
            if tipo == "" or "LONG":
                max_distancia = 0
                pendiente = 0
                for pareja in parejas_compra_venta:
                    
                    # Buscar le mas bajo
                    if not(pareja['compra']['ejecutada']) and abs(pareja['compra']['price']-future_ws.precio_actual) > max_distancia:
                        max_distancia = abs(pareja['compra']['price']-future_ws.precio_actual)
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
            if tipo == "" or "SHORT":
                max_distancia = 0
                pendiente = 0
                for pareja in parejas_compra_venta_short:
                    
                    # Buscar le mas alto
                    if not(pareja['venta']['ejecutada']) and abs(pareja['venta']['price']-future_ws.precio_actual) > max_distancia:
                        max_distancia = abs(pareja['venta']['price']-future_ws.precio_actual)
                        pareja_eliminar = pareja
                    
                    # Contar las parejas pendiente
                    if not(pareja['venta']['ejecutada']):
                        pendiente = pendiente + 1
                
                # Cancelar la orden sólo si hay mas de una
                if  pendiente > 1:
                                    
                    # Cancelar orden mas baja
                    future.cancelar_orden(exchange, activo, pareja_eliminar['venta']['orderId'])

                    # Remover la pareja mas baja
                    parejas_compra_venta_short.remove(pareja_eliminar)
    
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
        img_width, img_height = 450, 300*len(data)
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
        parejas_completadas = 0
        for pareja in data:
            ganancias_grid = ganancias_grid + pareja['general']['beneficios']
            if pareja['compra']['ejecutada'] and pareja['venta']['ejecutada']:
                parejas_completadas = parejas_completadas + 1

        draw.text((10, 70), f"Ganancias del grid:", font=font, fill=text_color)
        draw.text((180, 70), f"{round(ganancias_grid,3)} USDT ({round(100*ganancias_grid/balance_inicial,2)}%) ({parejas_completadas}/{len(data)})", font=font, fill=greenlight_color)

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
        if data == parejas_compra_venta:
            image.save('future/estrategias/infinity/output_long.png')
        if data == parejas_compra_venta_short:
            image.save('future/estrategias/infinity/output_short.png')

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
            
            # Cerrar posiciones
            posiciones = future.obtener_posicion(exchange, activo)
            for posicion in posiciones:
                # Long
                if posicion['positionIdx'] == 1:
                    if posicion['size'] != "0":
                        future.cerrar_posicion(exchange, activo, "LONG")
                # Short
                if posicion['positionIdx'] == 2:
                    if posicion['size'] != "0":
                        future.cerrar_posicion(exchange, activo, "SHORT")
            print("ORDENES Y POSICIONES CERRADAS!")
            print("")
        
        else:
            print("CERRANDO ESTRTATEGIA...")
            future.cancelar_orden(exchange, activo, orderId="")
            
            # Cerrar posiciones
            posiciones = future.obtener_posicion(exchange, activo)
            for posicion in posiciones:
                
                if posicion['positionIdx'] == 1 or posicion['positionIdx'] == 2:
                    if posicion['size'] != "0":
                        future.cerrar_posicion(exchange, activo, tipo.upper())
            print(f"ORDENES Y POSICIÓN {tipo.upper()} CERRADAS!")
            print("")

    except Exception as e:
        print("ERROR CERRANDO TODO")
        print(e)
        print("")
# -----------------------

# Función que detiene la estrategia por TP/SL
#--------------------------------------------
def detener_estrategia():
    try:

        # Variables globales
        global iniciar_estrategia

        # Ganancias del grid long
        ganancias_grid = 0
        if parejas_compra_venta != []:
            for pareja in parejas_compra_venta:
                ganancias_grid = ganancias_grid + pareja['general']['beneficios']
        
        # Ganancias del grid short
        ganancias_grid_short = 0
        if parejas_compra_venta_short != []:
            for pareja in parejas_compra_venta_short:
                ganancias_grid_short = ganancias_grid_short + pareja['general']['beneficios']

        # Detener estrategia por Take Profit
        if ((ganancia_actual() > 1.00369*tp and 100*(ganancias_grid+ganancias_grid_short)/balance_inicial > 1.00369*tp) or ganancia_actual() > 1.09*tp) and tp > 0:
            iniciar_estrategia = False
            cerrar_todo()
            mostrar_lista(parejas_compra_venta)
            mostrar_lista(parejas_compra_venta_short)
            print("ESTRATEGIA DETENIDA POR TP!!!")
            print("")

        # Detener estrategia por Stop Loss    
        if ganancia_actual() <= (-1)*(0.9*sl) and sl > 0:
            iniciar_estrategia = False
            cerrar_todo()
            mostrar_lista(parejas_compra_venta)
            mostrar_lista(parejas_compra_venta_short)
            print("ESTRATEGIA DETENIDA POR SL!!!")
            print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN detener_estrategia()")
        print(e)
        print("")
#--------------------------------------------

# Función auxiliar
#--------------------------------------------
def auxiliar():
    try:
        
        while iniciar_estrategia:

            # Mantener margen
            margen()

            # Gestionar la  dirección
            direccion()
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN auxiliar()")
        print(e)
        print("")
#--------------------------------------------

# Función que genera las direcciones
#-----------------------------------
def direccion():
    try:
        if tipo.upper() == "LONG":

            # Cancelar todas las ordenes short
            ordenes_abiertas = future.obtener_ordenes(exchange, activo)
            for orden in ordenes_abiertas:
                if orden['positionIdx'] == 2 and not(orden['reduceOnly']):
                    future.cancelar_orden(exchange, activo, orderId=orden['orderId'])
        
        if tipo.upper() == "SHORT":

            # Cancelar todas las ordenes long
            ordenes_abiertas = future.obtener_ordenes(exchange, activo)
            for orden in ordenes_abiertas:
                if orden['positionIdx'] == 1 and not(orden['reduceOnly']):
                    future.cancelar_orden(exchange, activo, orderId=orden['orderId'])
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN direccion()")
        print(e)
        print("")
#-----------------------------------

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
if 0.001 < precio_actual < 0.05:
    multiplo = 100
if precio_actual < 0.001:
    multiplo = 1000

# Inicializar las listas de parejas
parejas_compra_venta = []
parejas_compra_venta_short = []

# Iniciar hilo detener estrategia
hilo_detener_estrategia = threading.Thread(target=detener_estrategia)
hilo_detener_estrategia.daemon = True
hilo_detener_estrategia.start()

# Inicializar el grid
grid = []
if precio_referencia == 0:
    grid.append(precio_actual)
else:
    grid.append(precio_referencia)

# Iniciar Hilo que actualiza el grid
hilo_actualizar_grid = threading.Thread(target=actualizar_grid)
hilo_actualizar_grid.daemon = True
hilo_actualizar_grid.start()

# Cantidad de cada compra en USDT
cantidad_usdt, cantidad_usdt_short = parametros()

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

# Iniciar Hilo de las ordenes compra
hilo_ordenes_compra = threading.Thread(target=ordenes_compra, args=(exchange,activo))
hilo_ordenes_compra.daemon = True
hilo_ordenes_compra.start()

# Iniciar Hilo de las ordenes venta
hilo_ordenes_venta = threading.Thread(target=ordenes_venta, args=(exchange,activo))
hilo_ordenes_venta.daemon = True
hilo_ordenes_venta.start()

# Iniciar Hilo de las ordenes venta_short
hilo_ordenes_venta_short = threading.Thread(target=ordenes_venta_short, args=(exchange,activo))
hilo_ordenes_venta_short.daemon = True
hilo_ordenes_venta_short.start()

# Iniciar Hilo de las ordenes compra_short
hilo_ordenes_compra_short = threading.Thread(target=ordenes_compra_short, args=(exchange,activo))
hilo_ordenes_compra_short.daemon = True
hilo_ordenes_compra_short.start()

# Iniciar Hilo que limpia las listas
hilo_limpiar_listas = threading.Thread(target=limpiar_listas)
hilo_limpiar_listas.daemon = True
hilo_limpiar_listas.start()

# Iniciar Hilo auxiliar
hilo_auxiliar = threading.Thread(target=auxiliar)
hilo_auxiliar.daemon = True
hilo_auxiliar.start()

while iniciar_estrategia:
    try:

        # PARAMETROS DE LA ESTRATEGIA
        # ---------------------------
        # Abrir el archivo parametros.json y cargar su contenido
        parametros = json.load(open("future/estrategias/infinity/parametros_infinity_2.0.json", "r"))
        
        apalancamiento = parametros['apalancamiento']                                                       # Se recomienda un apalancamiento muy bajo para esta estrategia (<=3x)
        precio_referencia = parametros['precio_referencia']                                                 # Precio de referencia
        ganancia_grid = parametros['distancia_grid']+0.11                                                   # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
        cuenta = future.patrimonio(exchange=exchange)                                                       # Inversión de la estrategia
        tp = float(parametros['tp'])                                                                        # Take profit para detener la estrategia por completo
        sl = float(parametros['sl'])                                                                        # Stop Loss para detener la estrategia por completo
        tipo = parametros['direccion'].upper()                                                              # LONG o SHORT. Si se deja en blanco opera en ambas direcciones
        ganancia_grid_long = parametros['ganancia_grid_long']                                               # Ganancias por cada grid long
        ganancia_grid_short = parametros['ganancia_grid_short']                                             # Ganancias por cada grid short
        cantidad_usdt = cuenta*ganancia_grid_long/parametros['distancia_grid']                              # Importe en USDT para cada compra del long
        cantidad_usdt_short = cuenta*ganancia_grid_short/parametros['distancia_grid']                       # Importe en USDT para cada compra del short
        condicional_long = parametros['condicional_long']
        condicional_short = parametros['condicional_short']
        # ---------------------------

        # Verificar que el hilo detener_estrategia este activo
        if not(hilo_detener_estrategia.is_alive()):
            hilo_detener_estrategia = threading.Thread(target=detener_estrategia)
            hilo_detener_estrategia.daemon = True
            hilo_detener_estrategia.start()

        # Verificar que el hilo del precio actual este activo
        if not(hilo_precio_actual.is_alive) or future_ws.precio_actual == 0:
            hilo_precio_actual = threading.Thread(target=future_ws.precio_actual_activo, args=(exchange, activo))
            hilo_precio_actual.daemon = True
            hilo_precio_actual.start()

        # Verificar que el hilo actualizar grid este activo
        if not(hilo_actualizar_grid.is_alive()):
            hilo_actualizar_grid = threading.Thread(target=actualizar_grid)
            hilo_actualizar_grid.daemon = True
            hilo_actualizar_grid.start()

        # Verificar que el hilo limpiar listas este activo
        if not(hilo_limpiar_listas.is_alive()):
            hilo_limpiar_listas = threading.Thread(target=limpiar_listas)
            hilo_limpiar_listas.daemon = True
            hilo_limpiar_listas.start()

        # Verificar que el hilo auxiliar este activo
        if not(hilo_auxiliar.is_alive()):
            hilo_auxiliar = threading.Thread(target=auxiliar)
            hilo_auxiliar.daemon = True
            hilo_auxiliar.start()
        
        # LONG
        if tipo.upper() == "" or tipo.upper() == "LONG":
            
            # Verificar que el hilo de compras este activo
            if not(hilo_ordenes_compra.is_alive()):
                hilo_ordenes_compra = threading.Thread(target=ordenes_compra, args=(exchange,activo))
                hilo_ordenes_compra.daemon = True
                hilo_ordenes_compra.start()
            
            # Verificar que el hilo de venta este activo
            if not(hilo_ordenes_venta.is_alive()):
                hilo_ordenes_venta = threading.Thread(target=ordenes_venta, args=(exchange,activo))
                hilo_ordenes_venta.daemon = True
                hilo_ordenes_venta.start()
        
        # SHORT
        if tipo.upper() == "" or tipo.upper() == "SHORT":
            
            # Verificar que el hilo de compras este activo
            if not(hilo_ordenes_venta_short.is_alive()):
                hilo_ordenes_venta_short = threading.Thread(target=ordenes_venta_short, args=(exchange,activo))
                hilo_ordenes_venta_short.daemon = True
                hilo_ordenes_venta_short.start()
            
            # Verificar que el hilo de venta este activo
            if not(hilo_ordenes_compra_short.is_alive()):
                hilo_ordenes_compra_short = threading.Thread(target=ordenes_compra_short, args=(exchange,activo))
                hilo_ordenes_compra_short.daemon = True
                hilo_ordenes_compra_short.start()
    
    except Exception as e:
        print("ERROR EN EL PROGRAMA PRINCIPAL")
        print("")

cerrar_todo()
cerrar_todo()
mostrar_lista(parejas_compra_venta)
mostrar_lista(parejas_compra_venta_short)
cerrar_todo()
cerrar_todo()