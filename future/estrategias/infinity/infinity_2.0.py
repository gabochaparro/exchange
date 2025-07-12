''' 
Grid de futuros que imita el comportamiento del grid spot infinity de BingX.
La gran diferencia es que puedes aprovechar el apalancamiento para aumentar las ganancias.
El riesgo aumenta a medidas que icrementas el apalancamiento (recomiendo 3x máximo).
Pudes quemar la cuenta si desconoces la magnitud de las correcciones mercado.
'''

import future
import inverse
import inverse_ws
import future_ws
import json
import time
import threading
from datetime import datetime
import shutil
import os
import glob

# GESTIONAR ARCHIVOS DE PARAMETROS Y DE SALIDA
# --------------------------------------------
# Abrir el archivo parametros.json y cargar su contenido
parametros = json.load(open("future/estrategias/infinity/parametros_infinity_2.0.json", "r"))

# Especifica la ruta de la carpeta parametros
carpeta_parametros = 'future/estrategias/infinity/parametros/*'

# Usa glob para obtener todos los archivos dentro de la carpeta
archivos = glob.glob(carpeta_parametros)

# Elimina cada archivo en la carpeta
for archivo in archivos:
    try:
        if parametros['inverso']:
            if f"{parametros['activo'].upper()}_{parametros['exchange'].upper()}_INVERSO" in archivo:
                os.remove(archivo)
                print(f"{archivo} eliminado exitosamente.")
        else:
            if f"{parametros['activo'].upper()}_{parametros['exchange'].upper()}_LINEAL" in archivo:
                os.remove(archivo)
                print(f"{archivo} eliminado exitosamente.")
    except IsADirectoryError:
        print(f"{archivo} es una carpeta, omitiendo.")
    except FileNotFoundError:
        print(f"{archivo} no existe.")
    except PermissionError:
        print(f"No tienes permisos para eliminar {archivo}.")

# Especifica la ruta de la carpeta salida
carpeta_salida = 'future/estrategias/infinity/salida/*'

# Usa glob para obtener todos los archivos dentro de la carpeta
archivos = glob.glob(carpeta_salida)

# Elimina cada archivo en la carpeta
for archivo in archivos:
    try:
        os.remove(archivo)
        print(f"{archivo} eliminado exitosamente.")
    except IsADirectoryError:
        print(f"{archivo} es una carpeta, omitiendo.")
    except FileNotFoundError:
        print(f"{archivo} no existe.")
    except PermissionError:
        print(f"No tienes permisos para eliminar {archivo}.")

# Crear una copia temporal del archivo json con los parametros
fecha_inicio = int(time.time())*1000
if parametros['inverso']:
    parametros_copia = f"future/estrategias/infinity/parametros/{parametros['activo'].upper()}_{parametros['exchange'].upper()}_INVERSO_{fecha_inicio}.json"
else:
    parametros_copia = f"future/estrategias/infinity/parametros/{parametros['activo'].upper()}_{parametros['exchange'].upper()}_LINEAL_{fecha_inicio}.json"
shutil.copy("future/estrategias/infinity/parametros_infinity_2.0.json", parametros_copia)
# --------------------------------------------


# PARAMETROS DE LA ESTRATEGIA
# ---------------------------
parametros = json.load(open(parametros_copia, "r"))
exchange = parametros['exchange'].upper()                                                           # Exchange a utilizar
inverso = parametros['inverso']                                                                     # Futuros inversos (True/False)
activo = parametros['activo'].upper()                                                               # Activo a operar
apalancamiento = parametros['apalancamiento']                                                       # Se recomienda un apalancamiento muy bajo para esta estrategia (<=3x)
precio_referencia = parametros['precio_referencia']                                                 # Precio de referencia
comision_grid = 0.11
distancia_grid = parametros['distancia_grid']+comision_grid                                                  # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
tp = float(parametros['tp'])                                                                        # Take profit para detener la estrategia por completo
sl = float(parametros['sl'])                                                                        # Stop Loss para detener la estrategia por completo
tipo = parametros['direccion'].upper()                                                              # LONG o SHORT. Si se deja en blanco opera en ambas direcciones
ganancia_grid_long = parametros['ganancia_long']                                               # Ganancias por cada grid long
ganancia_grid_short = parametros['ganancia_short']
condicional_long = parametros['condicional_long']                                                   # Activar condicional de LONG
condicional_short = parametros['condicional_short']                                                 # Activar condicional de SHORT
umbral = parametros['umbral_libro']
auto = parametros['auto']
invertir_ganancias_grid = parametros['invertir_ganancias_grid']
breakeven = parametros['descarga_breakeven']
reiniciar_parejas = parametros['reiniciar_parejas']
precio_tp = parametros['precio_tp']
precio_sl = parametros['precio_sl']
proteccion_sl = False
# ---------------------------

# Cambiar el apalancamiento
if inverso:
    inverse.apalancamiento(exchange,activo,apalancamiento)
else:
    future.apalancamiento(exchange,activo,apalancamiento)

# Obtener el monto de la cuenta en USDT
if inverso:
    cuenta = inverse.patrimonio(exchange=exchange,symbol=activo)*inverse.precio_actual_activo(exchange,activo)  
else:
    cuenta = future.patrimonio(exchange=exchange)                                                   # Inversión de la estrategia

# Obtener importe de cada compra
cantidad_usdt = cuenta*ganancia_grid_long/distancia_grid                              # Importe en USDT para cada compra del long
cantidad_usdt_short = cuenta*ganancia_grid_short/distancia_grid                       # Importe en USDT para cada compra del short

# Definir el lote
if exchange == "BYBIT":
    lote = 1
    retraso_api = 2.7
if exchange == "BINANCE":
    lote = 100
    retraso_api = 7.92


# Función que actualiza el grid
# -----------------------------
def actualizar_grid():
    try:
        # variables globales y locales
        global grid

        while precio_actual != 0:
            #print(grid)

            # LONG
            while grid[-1] <= precio_actual != 0:
                
                # Agregar un nuevo nivel al grid
                nuevo_nivel = round(grid[-1]*(1+distancia_grid/100),decimales_precio)
                if nuevo_nivel not in grid:
                    grid.append(nuevo_nivel)
                
                # Grilla actualizada
                if grid[-1] > precio_actual and iniciar_estrategia == True:
                    print("")
                    print("Grilla Actualizada.")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")

            # SHORT
            while grid[0] >= precio_actual != 0:
                
                # Agregar un nuevo nivel al grid
                nuevo_nivel = round(grid[0]/(1+distancia_grid/100),decimales_precio)
                if nuevo_nivel not in grid:
                    grid.insert(0,nuevo_nivel)
                
                # Grilla actualizada
                if grid[0] < precio_actual and iniciar_estrategia == True:
                    print("")
                    print("Grilla Actualizada.")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")

            # Modificar el grid
            if not(precio_referencia in grid) and precio_referencia != 0:
                grid = []
                grid.append(precio_referencia)
                print("Generando nuevo grid...")
                print(grid)
            
            # Generar un nuevo grid
            if not(0.9*distancia_grid <= 100*abs(grid[0]-grid[1])/grid[0] <= 1.09*distancia_grid):
                grid = []
                if precio_referencia == 0:
                    grid.append(precio_actual)
                else:
                    grid.append(precio_referencia)
                print("Generando nuevo grid...")
                print(grid)
            
            time.sleep(0.36)
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN actualizar_grid()")
        print(e)
        print("")
# -----------------------------

# FUnción que se encarga de entrar la próxima compra y la próxima venta
# ---------------------------------------------------------------------
def prox_compra_venta():
    try:
        
        # Recorrer el grid y encontrar el próximo precio de compra y venta
        prox_compra = 0
        prox_venta = 0
        while prox_compra == 0 or prox_venta == 0:
            for grilla in grid:
                if grilla <= precio_actual < grilla*(1+distancia_grid/100):
                    prox_compra = grilla
                    if len(grid) > grid.index(grilla)+1:
                        prox_venta = grid[grid.index(grilla)+1]

        #print(prox_compra, prox_venta)
        return prox_compra, prox_venta
    
    except Exception as e:
        print("ERROR EN prox_compra_venta()")
        print(e)
        print("")
# ---------------------------------------------------------------------

# Función que verifica todos los parametros
# -----------------------------------------
def parametros():
    try:
        # Variables globales
        global apalancamiento

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
        if inverso:
            if apalancamiento > inverse.apalancamiento_max(exchange=exchange,symbol=activo):
                apalancamiento = inverse.apalancamiento_max(exchange=exchange,symbol=activo)
        else:
            if apalancamiento > future.apalancamiento_max(exchange=exchange,symbol=activo):
                apalancamiento = future.apalancamiento_max(exchange=exchange,symbol=activo)

        # Cantidad de la 1ra posicion a colocar
        cantidad_monedas = round((cantidad_usdt/precio_actual), decimales_moneda)
        cantidad_monedas_short = round((cantidad_usdt_short/precio_actual), decimales_moneda)
        if multiplo >= 1:
            cantidad_monedas = round(cantidad_monedas/multiplo)*multiplo
            cantidad_monedas_short = round(cantidad_monedas_short/multiplo)*multiplo
        
        # Imprimir Parametros
        print("")
        print("-----------------------------------------")
        if inverso:
            print("INFINITY 2.0 - FUTUROS - INVERSO")
        else:
            print("INFINITY 2.0 - FUTUROS")
        print("Exchange:", exchange.upper())
        print( "Activo:", activo.upper())
        if tipo == "":
            print("Dirección:", "LONG-SHORT")
        else:
            print("Dirección:", tipo.upper())
        if precio_referencia == 0:
            print("Precio de referencia:", precio_actual, "USDT")
        else:
            print("Precio de referencia:", precio_referencia, "USDT")
        if inverso:
            print("Cantidad de cada compra long:", round(cantidad_monedas,decimales_moneda), activo)
        else:
            print("Cantidad de cada compra long:", round(cantidad_usdt,2), "USDT")
        if inverso:
            print("Cantidad de cada compra short:", round(cantidad_monedas_short,decimales_moneda), activo)
        else:
            print("Cantidad de cada compra short:", round(cantidad_usdt_short,2), "USDT")
        print(f"Distancia entre cada grid: {round(distancia_grid-0.11,3)}%")
        print(f"Ganancas del grid long: {ganancia_grid_long}%")
        print(f"Ganancas del grid short: {ganancia_grid_short}%")
        print("Cuenta:", round(cuenta,2), "USDT")
        print(f"Apalancamiento: {apalancamiento}x")
        if inverso:
            print("Inversión inicial:", round(cuenta*apalancamiento,2), activo)
        else:
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
            return True
        
    except Exception as e:
        print("ERROR EN LA FUNCIÓN parametros()")
        print(e)
        print("")
        exit()
# -----------------------------------------

# Función que actualiza el estado de las parejas de compra y venta long
# ---------------------------------------------------------------------
def actualizar_pareja_long(exchange, symbol):
    try:

        ti = time.time()

        #Obtener historial de ordenes
        if inverso:
            historial_ordenes = inverse.obtener_historial_ordenes(exchange=exchange, symbol=symbol)
        else:
            historial_ordenes = future.obtener_historial_ordenes(exchange=exchange, symbol=symbol)
        
        # Recorrer las parejas long
        for pareja in parejas_compra_venta:
            if historial_ordenes != None:
                
                # Recorrer el historial de ordenes de compra
                for orden in historial_ordenes:
                    
                    # Obtener la orden de compra
                    if orden['orderId'] == pareja['compra']['orderId']:
                
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                        
                            # Actualizar la pareja
                            if orden['orderStatus'] == "Filled" and pareja['compra']['ejecutada'] == False:
                                if inverso:
                                    cantidad = orden['cumExecValue']
                                else:
                                    cantidad = orden['qty']
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['compra']['cantidad'] = str(cantidad)
                                pareja['compra']['price'] = str(orden['avgPrice'])
                                pareja['compra']['monto'] = str(float(pareja['compra']['cantidad'])*float(pareja['compra']['price']))
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                mostrar_lista(parejas_compra_venta)
                                break
                                
                        # BINANCE
                        if exchange.upper() == "BINANCE":
                        
                            # Actualizar pareja
                            if orden['status'] == "FILLED" and pareja['compra']['ejecutada'] == False:
                                if inverso:
                                    cantidad = orden['cumExecValue']
                                else:
                                    cantidad = orden['origQty']
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['compra']['cantidad'] = str(cantidad)
                                pareja['compra']['price'] = str(orden['avgPrice'])
                                pareja['compra']['monto'] = str(float(pareja['compra']['cantidad'])*float(pareja['compra']['price']))
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                mostrar_lista(parejas_compra_venta)
                                break
                
                # Recorrer el historial de ordenes de venta
                for orden in historial_ordenes:
                    
                    # Obtener la orden de venta
                    if orden['orderId'] == pareja['venta']['orderId']:
                        
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                        
                            # Actualizar pareja
                            if orden['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                if inverso:
                                    cantidad = float(pareja['compra']['cantidad'])*(1+(float(orden['avgPrice'])-float(pareja['compra']['price']))/float(pareja['compra']['price']))
                                else:
                                    cantidad = orden['qty']
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = str(cantidad)
                                pareja['venta']['price'] = str(orden['avgPrice'])
                                pareja['venta']['monto'] = str(float(pareja['venta']['cantidad'])*float(pareja['venta']['price']))
                                if inverso:
                                    pareja['general']['beneficios'] = str((1-comision_grid/100)*(float(pareja['venta']['cantidad'])-float(pareja['compra']['cantidad'])))
                                else:
                                    pareja['general']['beneficios'] = str((1-comision_grid/100)*(float(pareja['venta']['monto'])-float(pareja['compra']['monto'])))
                                
                                # Cancelar la orden de SL en caso tenga
                                if pareja['sl']['orderId'] != "":
                                    if inverso:
                                        inverse.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                        print("")
                                    else:
                                        future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                        print("")
                                
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                mostrar_lista(parejas_compra_venta)
                                break
                                
                        # BINANCE
                        if exchange.upper() == "BINANCE":
                        
                            # Actualizar pareja
                            if orden['status'] == "FILLED" and pareja['venta']['ejecutada'] == False:
                                if inverso:
                                    cantidad =  float(pareja['compra']['cantidad'])*(1+(float(orden['avgPrice'])-float(pareja['compra']['price']))/float(pareja['compra']['price']))
                                else:
                                    cantidad = orden['origQty']
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = str(cantidad)
                                pareja['venta']['price'] = str(orden['avgPrice'])
                                pareja['venta']['monto'] = str(float(pareja['venta']['cantidad'])*float(pareja['venta']['price']))
                                if inverso:
                                    pareja['general']['beneficios'] = str((1-comision_grid/100)*(float(pareja['venta']['cantidad'])-float(pareja['compra']['cantidad'])))
                                else:
                                    pareja['general']['beneficios'] = str((1-comision_grid/100)*(float(pareja['venta']['monto'])-float(pareja['compra']['monto'])))
                                
                                # Cancelar la orden de SL en caso tenga
                                if pareja['sl']['orderId'] != "":
                                    if inverso:
                                        inverse.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                        print("")
                                    else:
                                        future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                        print("")
                                
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                mostrar_lista(parejas_compra_venta)
                                break
                            
                    # Obtener la orden de sl
                    if orden['orderId'] == pareja['sl']['orderId']:
                        if exchange == "BYBIT":
                            if orden['orderStatus'] == "Filled":
                                
                                # Cancelar el tp en caso se haya tocado el SL y eliminira la pareja
                                if pareja in parejas_compra_venta:
                                    parejas_compra_venta.remove(pareja)
                                    print("Pareja removida por SL.", pareja)
                                    print("")
                                    mostrar_lista(parejas_compra_venta)
                                    if pareja['venta']['orderId'] != "":
                                        if inverso:
                                            inverse.cancelar_orden(exchange, activo, orderId=pareja['venta']['orderId'])
                                        else:
                                            future.cancelar_orden(exchange, activo, orderId=pareja['venta']['orderId'])
                                        print("TP Cancelado")
                                        print("")
                                    break

        if time.time()-ti < retraso_api:
            time.sleep(retraso_api)
        if time.time()-ti > 10.8:
            print("Parejas long actualizadas", round(time.time()-ti,2), "segundos")
    
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

        #Obtener historial de ordenes
        if inverso:
            historial_ordenes = inverse.obtener_historial_ordenes(exchange=exchange, symbol=symbol)
        else:
            historial_ordenes = future.obtener_historial_ordenes(exchange=exchange, symbol=symbol)
        
        for pareja in parejas_compra_venta_short:
            if historial_ordenes != None:
                
                # Obtener la orden de compra
                for orden in historial_ordenes:

                    # Obtener la orden de compra
                    if orden['orderId'] == pareja['compra']['orderId']:
                
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                        
                            # Acualizar la pareja
                            if orden['orderStatus'] == "Filled" and not(pareja['compra']['ejecutada']):
                                if inverso:
                                    cantidad = float(pareja['venta']['cantidad'])*(1+(float(pareja['venta']['price'])-float(orden['avgPrice']))/float(pareja['venta']['price']))
                                else:
                                    cantidad = orden['qty']
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['compra']['cantidad'] = str(cantidad)
                                pareja['compra']['price'] = str(orden['avgPrice'])
                                pareja['compra']['monto'] = str(float(pareja['compra']['cantidad'])*float(pareja['compra']['price']))
                                if inverso:
                                    pareja['general']['beneficios'] = str((1-comision_grid/100)*(float(pareja['venta']['cantidad'])-float(pareja['compra']['cantidad'])))
                                else:
                                    pareja['general']['beneficios'] = str((1-comision_grid/100)*(float(pareja['venta']['monto'])-float(pareja['compra']['monto'])))
                                    
                                # Cancelar la orden de SL en caso tenga
                                if pareja['sl']['orderId'] != "":
                                    if inverso:
                                        inverse.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                    else:
                                        future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                    print("SL Cancelado.")
                                    print("")
                                
                                #print(json.dumps(parejas_compra_venta_short,indent=2))
                                mostrar_lista(parejas_compra_venta_short)
                                break
                                
                        # BINANCE
                        if exchange.upper() == "BINANCE":
                        
                            # Actualizar la pareja
                            if orden['status'] == "FILLED" and pareja['compra']['ejecutada'] == False:
                                if inverso:
                                    cantidad = float(pareja['venta']['cantidad'])*(1+(float(pareja['venta']['price'])-float(orden['avgPrice']))/float(pareja['venta']['price']))
                                else:
                                    cantidad = orden['origQty']
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['compra']['cantidad'] = str(cantidad)
                                pareja['compra']['price'] = str(orden['avgPrice'])
                                pareja['compra']['monto'] = str(float(pareja['compra']['cantidad'])*float(pareja['compra']['price']))
                                if inverso:
                                    pareja['general']['beneficios'] = str((1-comision_grid/100)*(float(pareja['venta']['cantidad'])-float(pareja['compra']['cantidad'])))
                                else:
                                    pareja['general']['beneficios'] = str((1-comision_grid/100)*(float(pareja['venta']['monto'])-float(pareja['compra']['monto'])))
                                        
                                # Cancelar la orden de SL en caso tenga
                                if pareja['sl']['orderId'] != "":
                                    if inverso:
                                        inverse.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                    else:
                                        future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                    print("SL Cancelado.")
                                    print("")
                                
                                #print(json.dumps(parejas_compra_venta_short,indent=2))
                                mostrar_lista(parejas_compra_venta_short)
                                break
                            
                    # Obtener la orden de sl en BYBIT
                    if orden['orderId'] == pareja['sl']['orderId']:
                        if exchange == "BYBIT":
                            if orden['orderStatus'] == "Filled":
                                
                                # Cancelar la orden de compra en caso se haya tocado el SL y eliminar la pareja
                                if pareja in parejas_compra_venta:
                                    parejas_compra_venta.remove(pareja)
                                    print("Pareja removida por SL.", pareja)
                                    print("")
                                    mostrar_lista(parejas_compra_venta_short)
                                    if pareja['compra']['orderId'] != "":
                                        if inverso:
                                            inverse.cancelar_orden(exchange, activo, orderId=pareja['compra']['orderId'])
                                        else:
                                            future.cancelar_orden(exchange, activo, orderId=pareja['compra']['orderId'])
                                        print("TP cancelado")
                                        print("")
                                    break
                
                # Obtener la orden de venta
                for orden in historial_ordenes:
                        
                    # Obtener la orden de Venta
                    if orden['orderId'] == pareja['venta']['orderId']:
                
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                            
                            # Obtener la orden de venta en BYBIT
                            if orden['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                if inverso:
                                    cantidad = orden['cumExecValue']
                                else:
                                    cantidad = orden['qty']
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = str(cantidad)
                                pareja['venta']['price'] = str(orden['avgPrice'])
                                pareja['venta']['monto'] = str(float(pareja['venta']['cantidad'])*float(pareja['venta']['price']))
                                #print(json.dumps(parejas_compra_venta_short,indent=2))
                                mostrar_lista(parejas_compra_venta_short)
                                
                                break
                                
                        # BINANCE
                        if exchange.upper() == "BINANCE":
                    
                            # Obtener la orden de venta en Binance
                            if orden['status'] == "FILLED" and pareja['venta']['ejecutada'] == False:
                                if inverso:
                                    cantidad = orden['cumExecValue']
                                else:
                                    cantidad = orden['origQty']
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = str(cantidad)
                                pareja['venta']['price'] = str(orden['avgPrice'])
                                pareja['venta']['monto'] = str(float(pareja['venta']['cantidad'])*float(pareja['venta']['price']))
                                #print(json.dumps(parejas_compra_venta_short,indent=2))
                                mostrar_lista(parejas_compra_venta_short)
                                break

        if time.time()-ti < retraso_api:
            time.sleep(retraso_api)
        if time.time()-ti > 10.8:
            print("Parejas short actualizadas", round(time.time()-ti,2), "segundos")
    
    except Exception as e:
        print("ERROR EN LA FUNCION actualizar_pareja_short()")
        print(e)
        print("")
# ----------------------------------------------------------------------

# Función que limpia las parejas long
# --------------------------------------------
def limpiar_parejas_long():
    try:

        # Variables globales
        global parejas_compra_venta, parejas_compra_venta_short, posiciones, ordenes_abiertas
        
        while iniciar_estrategia:
            if parejas_compra_venta != [] or parejas_compra_venta_short != []:

                ti = time.time()
                
                # Obtener tamaño de la posición long
                size_long = "0"
                for posicion in posiciones:
                    
                    if exchange == "BYBIT":
                        if posicion['positionIdx'] == 0:
                            size_long = posicion['size']
                        
                        if posicion['positionIdx'] == 1:
                            size_long = posicion['size']
                    
                    if exchange == "BINANCE":
                        if posicion['positionSide'] == "LONG":
                            size_long = posicion['positionAmt']

                actualizar_pareja_long(exchange=exchange, symbol=activo)
                for pareja in parejas_compra_venta:
                    
                    # Limpiar la lista por falta de posición
                    if size_long == "0":
                        
                        if pareja['compra']['ejecutada'] and not(pareja['venta']['ejecutada']):
                        
                            # Verificar de nuevo la posición
                            if inverso:
                                posiciones = inverse.obtener_posicion(exchange, activo)
                            else:
                                posiciones = future.obtener_posicion(exchange, activo)
                            
                            for posicion in posiciones:
                                
                                if exchange == "BYBIT":
                                    if posicion['positionIdx'] == 0:
                                        size_long = posicion['size']
                                    
                                    if posicion['positionIdx'] == 1:
                                        size_long = posicion['size']

                                if exchange == "BINANCE":
                                    if posicion['positionSide'] == "LONG":
                                        size_long = posicion['positionAmt']
                            
                            if size_long == "0":
                                if pareja in parejas_compra_venta:
                                    parejas_compra_venta.remove(pareja)
                                    print("Pareja long removida por falta de posición!", pareja)
                                    print("")
                    
                    # Limpiar la lista por falta de orden
                    if not(pareja['compra']['ejecutada']):
                        
                        orden_puesta = False
                        if ordenes_abiertas != []:
                            
                            for orden in ordenes_abiertas:
                                
                                # Verificar si hay una orden limite
                                if 0.99*float(pareja['compra']['price']) <= float(orden['price']) <= 1.01*float(pareja['compra']['price']) and orden['side'].upper() == "BUY" and not(orden['reduceOnly']):
                                    orden_puesta = True
                                
                                if exchange == "BYBIT":
                                    # Verificar si hay una orden condicional
                                    if orden['triggerPrice'] != "":
                                        if 0.99*float(pareja['compra']['price']) <= float(orden['triggerPrice']) <= 1.01*float(pareja['compra']['price']) and orden['side'].upper() == "BUY" and not(orden['reduceOnly']) :
                                            orden_puesta = True
                                
                                if exchange == "BINANCE":
                                    # Verificar si hay una orden condicional
                                    if orden['stopPrice'] != "":
                                        if 0.99*float(pareja['compra']['price']) <= float(orden['stopPrice']) <= 1.01*float(pareja['compra']['price']) and orden['side'] == "BUY" and not(orden['reduceOnly']) :
                                            orden_puesta = True
                            
                        if not(orden_puesta):
                            actualizar_pareja_long(exchange=exchange, symbol=activo)
                            if not(pareja['compra']['ejecutada']):
                                if pareja in parejas_compra_venta:
                                    parejas_compra_venta.remove(pareja)
                                    print("Pareja long removida por falta de orden!", pareja)
                                    print("")
                    
                    # Limpiar la lista por falta de TP
                    if pareja['compra']['ejecutada'] and not(pareja['venta']['ejecutada']) and pareja['venta']['orderId'] != "":
                            
                        orden_puesta = False
                        if ordenes_abiertas != []:
                            for orden in ordenes_abiertas:
                                
                                # Verificar si hay una orden limite
                                if 0.99*float(pareja['venta']['price']) <= float(orden['price']) <= 1.01*float(pareja['venta']['price']) and orden['side'].upper() == "SELL" and orden['reduceOnly']:
                                    orden_puesta = True
                            
                        if not(orden_puesta):
                            actualizar_pareja_long(exchange=exchange, symbol=activo)
                            if pareja['compra']['ejecutada'] and not(pareja['venta']['ejecutada']):
                                if pareja in parejas_compra_venta:
                                    parejas_compra_venta.remove(pareja)
                                    print("Pareja long removida por falta de TP!", pareja)
                                    print("")

                if time.time()-ti < retraso_api:
                    time.sleep(retraso_api)

                if time.time()-ti > 60:
                    print("Parejas Long limpias", round(time.time()-ti, 2), "segundos")
                    print("")

    except Exception as e:
        print("ERROR EN LA FUNCIÓN limpiar_lista_long()")
        print(e)
        print("")
# --------------------------------------------

# Función que limpia las parejas short
# --------------------------------------------
def limpiar_parejas_short():
    try:

        # Variables globales
        global parejas_compra_venta, parejas_compra_venta_short, posiciones, ordenes_abiertas
        
        while iniciar_estrategia:
            if parejas_compra_venta != [] or parejas_compra_venta_short != []:

                ti = time.time()
                
                # Obtener tamaño de la posición short
                size_short = "0"
                for posicion in posiciones:
                    
                    if exchange == "BYBIT":
                        if posicion['positionIdx'] == 0:
                            size_short = posicion['size']
                        if posicion['positionIdx'] == 2:
                            size_short = posicion['size']
                    
                    if exchange == "BINANCE":
                        if posicion['positionSide'] == "SHORT":
                            size_short = posicion['positionAmt']

                # Obtener ordenes abiertas

                actualizar_pareja_short(exchange=exchange, symbol=activo)
                for pareja in parejas_compra_venta_short:
                    
                    # Limpiar la lista por falta de posición
                    if size_short == "0":
                        
                        if pareja['venta']['ejecutada'] and not(pareja['compra']['ejecutada']):

                            # Verificar de nuevo la posición
                            if inverso:
                                posiciones = inverse.obtener_posicion(exchange, activo)
                            else:
                                posiciones = future.obtener_posicion(exchange, activo)
                            
                            for posicion in posiciones:
                                
                                if exchange == "BYBIT":
                                    if posicion['positionIdx'] == 0:
                                        size_short = posicion['size']
                                    if posicion['positionIdx'] == 2:
                                        size_short = posicion['size']
                                
                                if exchange == "BINANCE":
                                    if posicion['positionSide'] == "SHORT":
                                        size_short = posicion['positionAmt']

                            if size_short == "0":
                                if pareja in parejas_compra_venta_short:                                              
                                    parejas_compra_venta_short.remove(pareja)
                                    print("Pareja short removida por falta de posición!", pareja)
                                    print("")
                    
                    # Limpiar la lista por falta de orden
                    if not(pareja['venta']['ejecutada']):
                        
                        orden_puesta = False
                        if ordenes_abiertas != []:
                            
                            # Verificar si estan puestas las ordenes
                            for orden in ordenes_abiertas:
                                
                                # Verificar si hay una orden limite
                                if 0.99*float(pareja['venta']['price']) <= float(orden['price']) <= 1.01*float(pareja['venta']['price']) and orden['side'].upper() == "SELL" and not(orden['reduceOnly']):
                                    orden_puesta = True
                                
                                # Verificar si hay una orden condicional
                                if exchange == "BYBIT":
                                    if orden['triggerPrice'] != "":
                                        if 0.99*float(pareja['venta']['price']) <= float(orden['triggerPrice']) <= 1.01*float(pareja['venta']['price']) and orden['side'].upper() == "SELL" and not(orden['reduceOnly']):
                                            orden_puesta = True
                                
                                if exchange == "BINANCE":
                                    if orden['stopPrice'] != "":
                                        if 0.99*float(pareja['venta']['price']) <= float(orden['stopPrice']) <= 1.01*float(pareja['venta']['price']) and orden['side'] == "SELL" and not(orden['reduceOnly']):
                                            orden_puesta = True
                            
                        if not(orden_puesta):
                            actualizar_pareja_short(exchange=exchange, symbol=activo)
                            if not(pareja['venta']['ejecutada']):
                                if pareja in parejas_compra_venta_short:
                                    parejas_compra_venta_short.remove(pareja)
                                    print("Pareja short removida por falta de orden!", pareja)
                                    print("")
                
                    # Limpiar la lista por falta de TP
                    if pareja['venta']['ejecutada'] and not(pareja['compra']['ejecutada']) and pareja['compra']['orderId'] != "":
                        
                        orden_puesta = False
                        if ordenes_abiertas != []:
                            
                            for orden in ordenes_abiertas:
                                
                                # Verificar si hay una orden limite
                                if 0.99*float(pareja['compra']['price']) <= float(orden['price']) <= 1.01*float(pareja['compra']['price']) and orden['side'].upper() == "BUY" and orden['reduceOnly']:
                                    orden_puesta = True
                            
                        if not(orden_puesta):
                            actualizar_pareja_short(exchange=exchange, symbol=activo)
                            if pareja['venta']['ejecutada'] and not(pareja['compra']['ejecutada']):
                                if pareja in parejas_compra_venta:
                                    parejas_compra_venta.remove(pareja)
                                    print("Pareja short removida por falta de TP!", pareja)
                                    print("")
                
                if time.time()-ti < retraso_api:
                    time.sleep(retraso_api)
                
                if time.time()-ti > 60:
                    print("Parejas short limpias", round(time.time()-ti, 2), "segundos")
                    print("")

    except Exception as e:
        print("ERROR EN LA FUNCIÓN limpiar_lista_short()")
        print(e)
        print("")
# --------------------------------------------

# Función que coloca las ordenes de compra para LONG
# --------------------------------------------------
def ordenes_compra(exchange, symbol):
    try:
        global precio_actual
        nueva_compra = 0
        nueva_venta = 0
        
        while iniciar_estrategia:

            if (tipo == "" or tipo == "LONG" or tipo == "RANGO") and not(pausa):
                
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
                actualizar_pareja_long(exchange=exchange, symbol=symbol)
                for pareja in parejas_compra_venta:
                    if not(pareja["venta"]['ejecutada']):

                        # Verificar la orden limite
                        if 0.999*float(pareja["compra"]['price']) < prox_compra < 1.001*float(pareja["compra"]['price']):
                            orden_compra_puesta = True
                        
                        # Verificar si tiene un TP
                        for orden in ordenes_abiertas:
                            if orden['reduceOnly'] and 0.999*prox_venta < float(orden['price']) < 1.001*prox_venta:
                                orden_compra_puesta = True
                        
                        # Verificar la orden condicional
                        if 0.999*float(pareja["compra"]['price']) < prox_venta < 1.001*float(pareja["compra"]['price']):
                            orden_condicional_compra_puesta = True
                        
                        # Verificar si tiene un TP
                        for orden in ordenes_abiertas:
                            if orden['reduceOnly'] and 0.999*(prox_venta*(1+distancia_grid/100)) < float(orden['price']) < 1.001*(prox_venta*(1+distancia_grid/100)):
                                orden_condicional_compra_puesta = True
                
                if precio_actual == 0:
                    # Consultar precio actual
                    if inverso:
                        precio_actual = inverse.precio_actual_activo(exchange=exchange, symbol=activo)
                    else:
                        precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
                
                # Cantidad de cada compra
                qty = round((cantidad_usdt/precio_actual),decimales_moneda)
                
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                if inverso:
                    qty = round(cantidad_usdt/lote)
                
                orden_compra = None
                
                # Colocar la orden limite de compra y crear la pareja de compra_veta
                if not(orden_compra_puesta):
                    if margen_disponible > cantidad_usdt > 0.9 and precio_actual > prox_compra:
                        if inverso:
                            orden_compra = inverse.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_compra, side="BUY", leverage=apalancamiento)
                        else:
                            orden_compra = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_compra, side="BUY", leverage=apalancamiento)
                        
                        if orden_compra != None:
                            time.sleep(3.06)
                            if inverso:
                                cantidad = lote*float(orden_compra['qty'])/float(orden_compra['price'])
                            else:
                                cantidad = orden_compra['qty']
                            parejas_compra_venta.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": "0"
                                                                    },
                                                        "compra": {
                                                                    "orderId": orden_compra['orderId'],
                                                                    "price": str(orden_compra['price']),
                                                                    "cantidad": str(cantidad),
                                                                    "monto": str(cantidad*float(orden_compra['price'])),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": "",
                                                                    "price": str(prox_venta),
                                                                    "cantidad": str(cantidad),
                                                                    "monto": str(cantidad*prox_venta),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                            actualizar_pareja_long(exchange=exchange, symbol=symbol)
                
                # Colocar la orden condicional de compra y crear la pareja de compra_veta
                if not(orden_condicional_compra_puesta) and condicional_long:
                    if margen_disponible > cantidad_usdt > 0.9 and precio_actual < prox_venta:
                        if inverso:
                            orden_compra = inverse.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_venta, side="BUY", leverage=apalancamiento)
                        else:
                            orden_compra = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_venta, side="BUY", leverage=apalancamiento)
                        
                        if orden_compra != None:
                            time.sleep(3.06)
                            if inverso:
                                cantidad = lote*float(orden_compra['qty'])/float(orden_compra['price'])
                            else:
                                cantidad = orden_compra['qty']
                            parejas_compra_venta.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": "0"
                                                                    },
                                                        "compra": {
                                                                    "orderId": orden_compra['orderId'],
                                                                    "price": str(orden_compra['price']),
                                                                    "cantidad": str(cantidad),
                                                                    "monto": str(cantidad*float(orden_compra['price'])),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": "",
                                                                    "price": str(prox_venta*(1+distancia_grid/100)),
                                                                    "cantidad": str(cantidad),
                                                                    "monto": str(cantidad*prox_venta*(1+distancia_grid/100)),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                            actualizar_pareja_long(exchange=exchange, symbol=symbol)
            
                # Imprimir cambios
                if orden_compra != None:
                    print("Grid Actual:")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")
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

            ti = time.time()
                        
            # Obtener posiciones
            if inverso:
                posiciones = inverse.obtener_posicion(exchange, activo)
            else:
                posiciones = future.obtener_posicion(exchange, activo)
            
            # Obtener el tamaño y el precio de la posición
            size = "0"
            for posicion in posiciones:
                
                if exchange == "BYBIT":
                    if posicion['positionIdx'] == 0:
                        size = posicion['size']
                        avgPrice = float(posicion['avgPrice'])
                    if posicion['positionIdx'] == 1:
                        size = posicion['size']
                        avgPrice = float(posicion['avgPrice'])

                if exchange == "BINANCE":
                    if posicion['positionSide'] == "LONG":
                        size = posicion['positionAmt']
                        avgPrice = float(posicion['entryPrice'])
                
            # Descarga en breakeven
            if not(breakeven):
                avgPrice = 0

            if size != "0" and posiciones != []:
            
                # Colocar la orden de venta
                for compra_venta in parejas_compra_venta:
                    if compra_venta["compra"]['ejecutada'] and compra_venta["venta"]['orderId'] == "":
                        
                        # Definir la cantidad
                        if inverso:
                            cantidad = round(float(compra_venta["venta"]['cantidad'])*float(compra_venta["venta"]['price'])/lote)*lote
                        else:
                            cantidad = compra_venta["venta"]['cantidad']
                        
                        # Colocar TP
                        orden = ""
                        if precio_actual < float(compra_venta["venta"]['price']) > 1.0011*avgPrice:
                            if inverso:
                                orden = inverse.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["venta"]['price'], type="LIMIT", tpSize=cantidad)
                            else:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["venta"]['price'], type="LIMIT", tpSize=cantidad)
                        
                        else:
                            if precio_actual > float(compra_venta["venta"]['price']) > 1.0011*avgPrice:
                                prox_compra, prox_venta = prox_compra_venta()
                                if inverso:
                                    orden = inverse.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=prox_venta, type="LIMIT", tpSize=cantidad)
                                else:
                                    orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=prox_venta, type="LIMIT", tpSize=cantidad)
                        
                        # Verificar que la respuesta sea válida antes de modificar la pareja
                        if orden != "":
                            time.sleep(3.6)
                            compra_venta["venta"]['orderId'] = orden['orderId']
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            print("")
                            #print(json.dumps(parejas_compra_venta,indent=2))
                        
                    # Colocar SL
                    if ganancia_actual() < -0.27 and float(compra_venta['compra']['price']) < precio_actual < float(compra_venta['venta']['price']) and compra_venta["sl"]['orderId'] == "" and proteccion_sl:
                        prox_compra, prox_venta = prox_compra_venta()
                        orden_sl = future.stop_loss(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=1.0001*prox_compra ,slSize=size)
                        
                        # Verificar que la respuesta sea válida antes de modificar la pareja
                        if orden_sl != None:
                            compra_venta["sl"]['orderId'] = orden_sl['orderId']
                            print("")
                            #print(json.dumps(parejas_compra_venta,indent=2))

            if time.time()-ti < retraso_api:
                time.sleep(retraso_api)
    
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_venta()")
        print(e)
        print("")
# ------------------------------------------------

# Función que coloca las ordenes de venta para SHORT
# --------------------------------------------------
def ordenes_venta_short(exchange, symbol):
    try:
        global precio_actual
        nueva_compra = 0
        nueva_venta = 0
        
        while iniciar_estrategia:

            if (tipo == "" or tipo == "SHORT" or tipo == "RANGO") and not(pausa):
                
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
                actualizar_pareja_short(exchange=exchange, symbol=symbol)
                for pareja in parejas_compra_venta_short:
                        if not(pareja["compra"]['ejecutada']):
                        
                            # Verificar orden limite
                            if 0.999*float(pareja["venta"]['price']) < prox_venta < 1.001*float(pareja["venta"]['price']):
                                orden_venta_puesta = True
                            for orden in ordenes_abiertas:
                                if orden['reduceOnly'] and 0.999*prox_compra < float(orden['price']) < 1.001*prox_compra:
                                    orden_venta_puesta = True
                                
                            # Verificar orden condicional
                            if 0.999*float(pareja["venta"]['price']) < prox_compra < 1.001*float(pareja["venta"]['price']):
                                orden_condicional_venta_puesta = True
                            for orden in ordenes_abiertas:
                                if orden['reduceOnly'] and 0.999*(prox_compra/(1+distancia_grid/100)) < float(orden['price']) < 1.001*(prox_compra/(1+distancia_grid/100)):
                                    orden_condicional_venta_puesta = True
                
                if precio_actual == 0:
                    # Consultar precio actual
                    if inverso:
                        precio_actual = inverse.precio_actual_activo(exchange=exchange, symbol=activo)
                    else:
                        precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
                
                # Cantidad de cada compra
                qty = round((cantidad_usdt_short/precio_actual),decimales_moneda)
                
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                if inverso:
                    qty = round(cantidad_usdt_short/lote)
                
                orden_venta = None
                
                # Colocar la orden limite de compra y crear la pareja de compra_veta
                if not(orden_venta_puesta):
                    if margen_disponible > cantidad_usdt_short > 0.9 and precio_actual < prox_venta:
                        if inverso:
                            orden_venta = inverse.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_venta, side="SELL", leverage=apalancamiento)
                        else:
                            orden_venta = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_venta, side="SELL", leverage=apalancamiento)
                        
                        if orden_venta != None:
                            time.sleep(3.06)
                            if inverso:
                                cantidad = lote*float(orden_venta['qty'])/float(orden_venta['price'])
                            else:
                                cantidad = orden_venta['qty']
                            parejas_compra_venta_short.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": "0"
                                                                    },
                                                        "compra": {
                                                                    "orderId": "",
                                                                    "price": str(prox_compra),
                                                                    "cantidad": str(cantidad),
                                                                    "monto": str(cantidad*prox_compra),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": orden_venta['orderId'],
                                                                    "price": str(orden_venta['price']),
                                                                    "cantidad": str(cantidad),
                                                                    "monto": str(cantidad*float(orden_venta['price'])),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                            actualizar_pareja_short(exchange=exchange, symbol=symbol)
                
                # Colocar la orden condicional de compra y crear la pareja de compra_veta
                if not(orden_condicional_venta_puesta) and condicional_short:
                    if margen_disponible > cantidad_usdt_short > 0.9 and precio_actual > prox_compra:
                        if inverso:
                            orden_venta = inverse.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_compra, side="SELL", leverage=apalancamiento)
                        else:
                            orden_venta = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_compra, side="SELL", leverage=apalancamiento)
                        
                        if orden_venta != None:
                            time.sleep(3.06)
                            if inverso:
                                cantidad = lote*float(orden_venta['qty'])/float(orden_venta['price'])
                            else:
                                cantidad = orden_venta['qty']
                            parejas_compra_venta_short.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": "0"
                                                                    },
                                                        "compra": {
                                                                    "orderId": "",
                                                                    "price": str(prox_compra/(1+distancia_grid/100)),
                                                                    "cantidad": str(cantidad),
                                                                    "monto": str(cantidad*prox_compra/(1+distancia_grid/100)),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": orden_venta['orderId'],
                                                                    "price": str(orden_venta['price']),
                                                                    "cantidad": str(cantidad),
                                                                    "monto": str(cantidad*float(orden_venta['price'])),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                            actualizar_pareja_short(exchange=exchange, symbol=symbol)
                
                # Imprimir cambios
                if orden_venta != None:
                    print("Grid Actual:")
                    print(grid)
                    print("Cantidad de grillas:", len(grid))
                    print("")
                    #print(json.dumps(parejas_compra_venta_short,indent=2))

    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_compra()")
        print(e)
        print("")
# --------------------------------------------------

# Función que coloca lsa ordenes de compra para SHORT
# --------------------------------------------------
def ordenes_compra_short(exchange, symbol):
    try:
        while iniciar_estrategia:

            ti = time.time()
                            
            # Obtener posiciones
            if inverso:
                posiciones = inverse.obtener_posicion(exchange, activo)
            else:
                posiciones = future.obtener_posicion(exchange, activo)
            
            # Obtener el tamaño y el precio de la posición
            size = "0"
            for posicion in posiciones:
                
                if exchange == "BYBIT":
                    if posicion['positionIdx'] == 0:
                        size = posicion['size']
                        avgPrice = float(posicion['avgPrice'])
                    if posicion['positionIdx'] == 2:
                        size = posicion['size']
                        avgPrice = float(posicion['avgPrice'])
                
                if exchange == "BINANCE":
                    if posicion['positionSide'] == "SHORT":
                        size = posicion['positionAmt']
                        avgPrice = float(posicion['entryPrice'])
            
            # Descarga en breakeven
            if not(breakeven):
                avgPrice = 1000000000
            
            # Colocar el SL y el TP solo si existe una posición
            if size != "0" and posiciones != []:
            
                # Colocar la orden de compra y actualiza la pareja de compra_veta
                for compra_venta in parejas_compra_venta_short:
                    if compra_venta["venta"]['ejecutada'] and compra_venta["compra"]['orderId'] == "":
                        
                        # Definir cantidad
                        if inverso:
                            cantidad = round(float(compra_venta["compra"]['cantidad'])*float(compra_venta["venta"]['price'])/lote)*lote
                        else:
                            cantidad = compra_venta["compra"]['cantidad']
                        
                        # Colocar TP
                        orden = ""
                        if precio_actual > float(compra_venta["compra"]['price']) < 0.999*avgPrice:
                            if inverso:
                                orden = inverse.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=compra_venta["compra"]['price'], type="LIMIT",tpSize=cantidad)
                            else:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=compra_venta["compra"]['price'], type="LIMIT",tpSize=cantidad)
                        
                        else:
                            if precio_actual < float(compra_venta["compra"]['price']) < 0.999*avgPrice:
                                prox_compra, prox_venta = prox_compra_venta()
                                if inverso:
                                    orden = inverse.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=prox_compra, type="LIMIT", tpSize=cantidad)
                                else:
                                    orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=prox_compra, type="LIMIT", tpSize=cantidad)
                                
                        # Verificar que la respuesta sea válida antes de modificar la pareja
                        if orden != "":
                            time.sleep(3.6)
                            compra_venta["compra"]['orderId'] = orden['orderId']
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            print("")
                            #print(json.dumps(parejas_compra_venta_short,indent=2))
                        
                    # Colocar SL
                    if ganancia_actual() < -0.27 and float(compra_venta['compra']['price']) < precio_actual < float(compra_venta['venta']['price']) and compra_venta["sl"]['orderId'] == "" and proteccion_sl:
                        prox_compra, prox_venta = prox_compra_venta()
                        orden_sl = future.stop_loss(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=0.9999*prox_venta ,slSize=size)
                        
                        # Verificar que la respuesta sea válida antes de modificar la pareja
                        if orden_sl != None:
                            compra_venta["sl"]['orderId'] = orden_sl['orderId']
                            print("")
                            #print(json.dumps(parejas_compra_venta,indent=2))

                    if time.time()-ti < retraso_api:
                        time.sleep(retraso_api)
                        
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_compra_short()")
        print(e)
        print("")
# --------------------------------------------------

# Función que mantiene la disponibilidad del margen
# -------------------------------------------------
def margen():
    try:
        global margen_disponible

        # Verificar si no hay margen disponible para la compra
        if inverso:
            margen_disponible = inverse.margen_disponible(exchange,activo)*apalancamiento*precio_actual
        else:
            margen_disponible = future.margen_disponible(exchange)*apalancamiento
        
            
        # LONG
        if tipo == "" or "LONG":
            if margen_disponible < cantidad_usdt:
                
                max_distancia = 0
                pendiente = 0
                for pareja in parejas_compra_venta:
                    
                    # Buscar le mas bajo
                    if not(pareja['compra']['ejecutada']) and abs(float(pareja['compra']['price'])-precio_actual) > max_distancia:
                        max_distancia = abs(float(pareja['compra']['price'])-precio_actual)
                        pareja_eliminar = pareja
                    
                    # Contar las parejas pendiente
                    if not(pareja['compra']['ejecutada']):
                        pendiente = pendiente + 1
                
                # Cancelar la orden sólo si hay mas de una
                if  pendiente > 1:
                    
                    # Cancelar orden mas baja
                    if inverso:
                        inverse.cancelar_orden(exchange, activo, pareja_eliminar['compra']['orderId'])
                    else:
                        future.cancelar_orden(exchange, activo, pareja_eliminar['compra']['orderId'])

                    # Remover la pareja mas baja
                    if pareja_eliminar in parejas_compra_venta:
                        parejas_compra_venta.remove(pareja_eliminar)
            
        # SHORT
        if tipo == "" or "SHORT":
            if margen_disponible < cantidad_usdt_short:
                
                max_distancia = 0
                pendiente = 0
                for pareja in parejas_compra_venta_short:
                    
                    # Buscar le mas alto
                    if not(pareja['venta']['ejecutada']) and abs(float(pareja['venta']['price'])-precio_actual) > max_distancia:
                        max_distancia = abs(float(pareja['venta']['price'])-precio_actual)
                        pareja_eliminar = pareja
                    
                    # Contar las parejas pendiente
                    if not(pareja['venta']['ejecutada']):
                        pendiente = pendiente + 1
                
                # Cancelar la orden sólo si hay mas de una
                if  pendiente > 1:
                                    
                    # Cancelar orden mas baja
                    if inverso:
                        inverse.cancelar_orden(exchange, activo, pareja_eliminar['venta']['orderId'])
                    else:
                        future.cancelar_orden(exchange, activo, pareja_eliminar['venta']['orderId'])

                    # Remover la pareja mas baja
                    if pareja_eliminar in parejas_compra_venta_short:
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
        ti = time.time()

        # Ganancia actual
        ganancia = ganancia_actual()

        # Calcular ganancias del grid       
        ganancias_grid = 0
        parejas_completadas = 0
        if data != []:
            for pareja in data:
                ganancias_grid = ganancias_grid + float(pareja['general']['beneficios'])
                if pareja['compra']['ejecutada'] and pareja['venta']['ejecutada']:
                    parejas_completadas = parejas_completadas + 1

        # Crea un archivo json con la info de las parejas
        balance_actual = cuenta
        if inverso:
            balance_actual = cuenta/precio_actual
        salida = {
                        'fecha_inicio': str(fecha_inicio),
                        'exchange': exchange,
                        'activo': activo,
                        'inverso': inverso,
                        'balance_inicial': str(balance_inicial),
                        'balance_actual': str(balance_actual),
                        'ganancias_del_grid': str(ganancias_grid),
                        'ganancia_actual': str(ganancia),
                        'riesgo_maximo': str(riesgo_max),
                        'beneficio_maximo': str(beneficio_max),
                        'cantidad_parejeas': str(len(data)),
                        'parejas_completadas': str(parejas_completadas),
                        'parejas': data
                        }
        
        if data == parejas_compra_venta:
            if inverso:
                ruta = f'future/estrategias/infinity/salida/{activo}_{exchange}_INVERSO_{fecha_inicio}_LONG.json'
            else:
                ruta = f'future/estrategias/infinity/salida/{activo}_{exchange}_LINEAL_{fecha_inicio}_LONG.json'
            json.dump(salida, open(ruta, "w"), indent=4)
        
        if data == parejas_compra_venta_short:
            if inverso:
                ruta = f'future/estrategias/infinity/salida/{activo}_{exchange}_INVERSO_{fecha_inicio}_SHORT.json'
            else:
                ruta = f'future/estrategias/infinity/salida/{activo}_{exchange}_LINEAL_{fecha_inicio}_SHORT.json'
            json.dump(salida, open(ruta, "w"), indent=4)        
        
        if time.time()-ti < retraso_api:
                time.sleep(retraso_api)
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN mostrar_lista()")
        print(e)
        print("")
# -----------------------------------------------------

# Funciôn que gestiona la impresión de las parejas
# ------------------------------------------------
def imprimir_parejas():
    try:
        monitor = cuenta
        
        while iniciar_estrategia:

            # Mostrar parejas
            if monitor != cuenta:
                monitor = cuenta
                mostrar_lista(parejas_compra_venta)
                mostrar_lista(parejas_compra_venta_short)


    except Exception as e:
        print("ERROR EN LA FUNCIÓN imprimir_parejas()")
# ------------------------------------------------

# Función que mide la ganancia actual (en porcentaje %)
# -----------------------------------------------------
def ganancia_actual():
    try:
        # Variables globales
        global posiciones, precio_actual

        # Obtener posiciones
        size = 0
        for posicion in posiciones:
            
            # Obtener el tamaño de las posiciones
            if exchange == "BYBIT":
                if posicion['positionIdx'] == 0:
                    size = size + float(posicion['size'])
                if posicion['positionIdx'] == 1:
                    size = size + float(posicion['size'])
                if posicion['positionIdx'] == 2:
                    size = size + float(posicion['size'])
            
            if exchange == "BINANCE":
                if posiciones != []:
                    if posicion['positionSide'] == "LONG":
                        size = size + float(posicion['positionAmt'])
                    if posicion['positionSide'] == "SHORT":
                        size = size + float(posicion['positionAmt'])
        
        # Comisión por cierre a market
        comision_cierre = 0.1/100
        if exchange == "BYBIT":
            comision_cierre = 0.1/100
        if exchange == "BINANCE":
            comision_cierre = 0.1/100
        
        if precio_actual == 0:
            # Consultar precio actual
            if inverso:
                precio_actual = inverse.precio_actual_activo(exchange=exchange, symbol=activo)
            else:
                precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)

        if inverso:
            return 100*((inverse.patrimonio(exchange,activo)-(size/precio_actual)*comision_cierre) - balance_inicial)/balance_inicial
        else:
            return 100*((future.patrimonio(exchange)-size*precio_actual*comision_cierre) - balance_inicial)/balance_inicial

    except Exception  as e:
        print("ERROR EN LA FUNCIÓN ganancia_actual()")
        print(e)
        print("")
# -----------------------------------------------------

# Función que cierra todo
# -----------------------
def cerrar_todo():
    try:

        print("CERRANDO ESTRTATEGIA...")
        
        # Cancelar todas las ordenes
        if inverso:
            inverse.cancelar_orden(exchange, activo, orderId="")
        else:
            future.cancelar_orden(exchange, activo, orderId="")
        
        # Cerrar posiciones
        if inverso:
            posiciones = inverse.obtener_posicion(exchange, activo)
        else:
            posiciones = future.obtener_posicion(exchange, activo)
        for posicion in posiciones:
            
            if exchange == "BYBIT":
                # Long
                if posicion['positionIdx'] == 0 and posicion['side'] == "Buy":
                    if posicion['size'] != "0":
                        if inverso:
                            inverse.cerrar_posicion(exchange, activo, "LONG")
                        else:
                            future.cerrar_posicion(exchange, activo, "LONG")
                
                if posicion['positionIdx'] == 1:
                    if posicion['size'] != "0":
                        if inverso:
                            inverse.cerrar_posicion(exchange, activo, "LONG")
                        else:
                            future.cerrar_posicion(exchange, activo, "LONG")
                # Short
                if posicion['positionIdx'] == 0 and posicion['side'] == "Sell":
                    if posicion['size'] != "0":
                        if inverso:
                            inverse.cerrar_posicion(exchange, activo, "SHORT")
                        else:
                            future.cerrar_posicion(exchange, activo, "SHORT")
                
                if posicion['positionIdx'] == 2:
                    if posicion['size'] != "0":
                        if inverso:
                            inverse.cerrar_posicion(exchange, activo, "SHORT")
                        else:
                            future.cerrar_posicion(exchange, activo, "SHORT")
            
            if exchange == "BINANCE":
                if posiciones != []:
                    # Long
                    if posicion['positionSide'] == "LONG":
                        if posicion['notional'] != "0":
                            if inverso:
                                inverse.cerrar_posicion(exchange, activo, "LONG")
                            else:
                                future.cerrar_posicion(exchange, activo, "LONG")
                    # Short
                    if posicion['positionSide'] == "SHORT":
                        if posicion['notional'] != "0":
                            if inverso:
                                inverse.cerrar_posicion(exchange, activo, "SHORT")
                            else:
                                future.cerrar_posicion(exchange, activo, "SHORT")
        
        print("ORDENES Y POSICIONES CERRADAS!")
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
        global iniciar_estrategia, riesgo_max, beneficio_max, pausa, balance_inicial, parejas_compra_venta, parejas_compra_venta_short

        ti = time.time()

        # Ganancia actual
        beneficio = ganancia_actual()
        
        # Riesgo máximo alcanzado
        if 0 > beneficio < riesgo_max:
            riesgo_max = beneficio
        
        # Beneficio máximo alcanzado
        if 0 < beneficio > beneficio_max:
            beneficio_max = beneficio

        # Ganancias del grid long
        ganancias_grid = 0
        if parejas_compra_venta != []:
            for pareja in parejas_compra_venta:
                ganancias_grid = ganancias_grid + float(pareja['general']['beneficios'])
        
        # Ganancias del grid short
        ganancias_grid_short = 0
        if parejas_compra_venta_short != []:
            for pareja in parejas_compra_venta_short:
                ganancias_grid_short = ganancias_grid_short + float(pareja['general']['beneficios'])

        # Detener estrategia por Take Profit
        if (beneficio > tp  and tp != float(0)) or (precio_actual > precio_tp and precio_tp != float(0) and tipo == "LONG") or (precio_actual < precio_tp and precio_tp != float(0) and tipo == "SHORT"):
            pausa = True
            parametros['pausa'] = True
            json.dump(parametros, open(parametros_copia, "w"), indent=4)
            cerrar_todo()
            mostrar_lista(parejas_compra_venta)
            mostrar_lista(parejas_compra_venta_short)
            cerrar_todo()
            print("ESTRATEGIA PAUSADA POR TP!!!")
            print("")

        # Detener estrategia por Stop Loss    
        if (beneficio <= (-1)*(0.9*sl) and sl != float(0)) or (precio_actual <= precio_sl and precio_sl != float(0) and tipo == "LONG") or (precio_actual >= precio_sl and precio_sl != float(0) and tipo == "SHORT"):
            iniciar_estrategia = False
            cerrar_todo()
            mostrar_lista(parejas_compra_venta)
            mostrar_lista(parejas_compra_venta_short)
            print("ESTRATEGIA DETENIDA POR SL!!!")
            print("")

        # Retraso por hiperactividad
        if time.time()-ti < retraso_api:
            time.sleep(0.9)
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN detener_estrategia()")
        print(e)
        print("")
#--------------------------------------------

# FUNCIÓN QUE DETECTA LA TENDENCIA DE UN ACTIVO
# ---------------------------------------------
def detectar_tendencia(exchange, symbol):
    try:
        global tendencia_detector
    
        from binance.client import Client
        from pybit.unified_trading import HTTP
        import threading
        import time

        client = Client(api_key="", api_secret="", tld="com")
        session = HTTP(testnet=False)


        # CONFIGURACIÓN DE PARAMETROS
        #----------------------------------------------
        exchange = exchange.upper()
        symbol = symbol.upper()+"USDT"
        cantidad_velas = 3
        intervalos = ["1M","5M","1H","4H","1D","1S"]
        #----------------------------------------------

        # FUNCIÓN PARA OBTENER LAS ÚLTIMAS X VELAS DEL PRECIO DE UN PAR EN DETERMINADO INTERVALO
        #---------------------------------------------------------------------------------------
        def obtener_velas_precio(symbol,interval):
            try:

                symbol = symbol.upper()
                interval = interval.upper()

                # BINANCE
                if exchange.upper() == "BINANCE":
                    
                    # Definir intervalos
                    if interval == "1M":
                        interval = Client.KLINE_INTERVAL_1MINUTE
                    if interval == "5M":
                        interval = Client.KLINE_INTERVAL_5MINUTE
                    if interval == "30M":
                        interval = Client.KLINE_INTERVAL_30MINUTE
                    if interval == "1H":
                        interval = Client.KLINE_INTERVAL_1HOUR
                    if interval == "4H":
                        interval = Client.KLINE_INTERVAL_4HOUR
                    if interval == "1D":
                        interval = Client.KLINE_INTERVAL_1DAY
                    if interval == "1S":
                        interval = Client.KLINE_INTERVAL_1WEEK
                    
                    # Obtener las velas
                    velas = client.futures_klines(symbol=symbol, interval=interval, limit=cantidad_velas)
                    #print(velas)
                
                # BYBIT
                if exchange.upper() == "BYBIT":
                    
                    # Definir intervalos
                    if interval == "1M":
                        interval = "1"
                    if interval == "5M":
                        interval = "5"
                    if interval == "30M":
                        interval = "30"
                    if interval == "1H":
                        interval = "60"
                    if interval == "4H":
                        interval = "240"
                    if interval == "1D":
                        interval = "D"
                    if interval == "1S":
                        interval = "W"
                
                    # Obtener las velas
                    if inverso:
                        velas = session.get_kline(category="inverse", symbol=symbol, interval=interval, limit=cantidad_velas)['result']['list']
                    else:
                        velas = session.get_kline(category="linear", symbol=symbol, interval=interval, limit=cantidad_velas)['result']['list']

                velas.sort()
                return velas
            
            except Exception as e:
                print("ERROR EN LA FUNCIÓN: obtener_velas_precio()")
                print(e)
                print("")
                velas = []
                return velas
        #---------------------------------------------------------------------------------------
        
        # FUNCIÓN QUE BUSCA LA SERIE DE VELAS
        # -----------------------------------
        def serie_velas():
            try:
                lista_velas = []
                for intervalo in intervalos:
                    lista_velas.append(obtener_velas_precio(symbol,intervalo))
                
                #print("Nueva Serie de Velas")
                return lista_velas
            
            except Exception as e:
                print("ERROR EN LA FUNCIÓN velas()")
                print(e)
                print("")
        # -----------------------------------

        # FUNCIÓN QUE DETERMINA LA TENDENCIA SEGÚN LAS VELAS
        # --------------------------------------------------
        def tendencia(velas):
            try:
                if len(velas) > 2:
                    # Inicializar variables
                    vela_inicial_apertura = float(velas[0][1])
                    vela_medio_apertura = float(velas[1][1])
                    vela_medio_cierre = float(velas[1][4])
                    vela_final_cierre = precio_actual
                    
                    if (vela_medio_cierre > vela_inicial_apertura) and (vela_final_cierre > vela_medio_apertura):
                        return "ALCISTA"
                    if (vela_medio_cierre < vela_inicial_apertura) and (vela_final_cierre < vela_medio_apertura):
                        return "BAJISTA"
                
                return "RANGO"
            
            except Exception as e:
                print("ERROR EN LA FUNCIÓN tendencia()")
                print(e)
                print("")
        # --------------------------------------------------

        # FUNCIÓN QUE DETERMINA LA TENDENCIA TOTAL
        # ----------------------------------------
        def detector(serie_velas):
            try:
                alcistas = 0
                bajistas = 0
                for velas in serie_velas:
                    direccion = tendencia(velas)
                    if direccion == "ALCISTA":
                        alcistas = alcistas + 1
                    if direccion == "BAJISTA":
                        bajistas = bajistas + 1

                if 3 <= alcistas > bajistas:
                    return "ALCISTA", alcistas, "BAJISTA", bajistas
                
                if 3 <= bajistas > alcistas:
                    return "BAJISTA", bajistas, "ALCISTA", alcistas
                
                return "RANGO", "ALCISTA", alcistas, "BAJISTA", bajistas

            except Exception as e:
                print("ERROR EN LA FUNCIÓN detector()")
        # ----------------------------------------

        while iniciar_estrategia:
            serie = serie_velas()
            tendencia_detector = detector(serie)
            time.sleep(1)

    except Exception as e:
        print("ERROR EN LA FUNCIÓN detectar_tendencia()")
        print(e)
        print("")
# ---------------------------------------------

# Función que gestiona la dirección
#----------------------------------
def direccion():
    try:

        # Variables globales
        global cantidad_usdt, cantidad_usdt_short, libro

        # Invertir ganancias del grid
        if ganancia_grid_long > ganancia_grid_short:
            mayor = ganancia_grid_long
            menor = ganancia_grid_short
        else:
            mayor = ganancia_grid_short
            menor = ganancia_grid_long
        
        # Cambiar la dirección a LONG
        if libro == "LONG" or (tendencia_detector[0] == "ALCISTA" and libro == ""):
            if tipo != "LONG":
                if auto:
                    print("Cambio de tendencia!", tendencia_detector[0])
                    print("")
                    parametros['direccion'] = "LONG"
                    if invertir_ganancias_grid:
                        parametros['ganancia_long'] = mayor
                        parametros['ganancia_short'] = menor
                    json.dump(parametros, open(parametros_copia, "w"), indent=4)
            
        # Cambiar la dirección a SHORT
        if libro == "SHORT" or (tendencia_detector[0] == "BAJISTA" and libro == ""):
            if tipo != "SHORT":
                if auto:
                    print("Cambio de tendencia!", tendencia_detector[0])
                    print("")
                    parametros['direccion'] = "SHORT"
                    if invertir_ganancias_grid:
                        parametros['ganancia_long'] = menor
                        parametros['ganancia_short'] = mayor
                    json.dump(parametros, open(parametros_copia, "w"), indent=4)
            
        # Cambiar la dirección a RANGO
        if tendencia_detector[0] == "RANGO" and libro == "":
            if tipo != "RANGO":
                if auto:
                    print("Cambio de tendencia!", tendencia_detector[0])
                    print("")
                    parametros['direccion'] = "RANGO"
                    json.dump(parametros, open(parametros_copia, "w"), indent=4)

        # Cancelar todas las ordenes short
        if tipo == "LONG" or pausa:
            for orden in ordenes_abiertas:
                
                if exchange == "BYBIT":
                    if orden['side'] == "Sell" and not(orden['reduceOnly']):
                        if inverso:
                            inverse.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                        else:
                            future.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                
                if exchange == "BINANCE":
                    if orden['positionSide'] == "SHORT" and not(orden['reduceOnly']):
                        if inverso:
                            inverse.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                        else:
                            future.cancelar_orden(exchange, activo, orderId=orden['orderId'])

        # Cancelar todas las ordenes long
        if tipo == "SHORT" or pausa:
            for orden in ordenes_abiertas:
                
                if exchange == "BYBIT":
                    if orden['side'] == "Buy" and not(orden['reduceOnly']):
                        if inverso:
                            inverse.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                        else:
                            future.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                
                if exchange == "BINANCE":
                    if orden['positionSide'] == "LONG" and not(orden['reduceOnly']):
                        if inverso:
                            inverse.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                        else:
                            future.cancelar_orden(exchange, activo, orderId=orden['orderId'])
     
    except Exception as e:
        print("ERROR EN LA FUNCIÓN direccion()")
        print(e)
        print("")
#----------------------------------

# Función que equilibria las posiciones y los take profit
# -------------------------------------------------------
def equilibrio():
    try:

        # Obtener la posición
        if inverso:
            posiciones = inverse.obtener_posicion(exchange, activo)
        else:
            posiciones = future.obtener_posicion(exchange, activo)
    
    # LONG
        size = 0
        for posicion in posiciones:

            if exchange == "BYBIT":
                if posicion['positionIdx'] == 0:
                    if posicion['size'] != "0":
                        size = float(posicion['size'])
                        avgPrice = float(posicion['avgPrice'])
                        #print("size long", size)
                        #print("")
                if posicion['positionIdx'] == 1:
                    if posicion['size'] != "0":
                        size = float(posicion['size'])
                        avgPrice = float(posicion['avgPrice'])
                        #print("size long", size)
                        #print("")

            if exchange == "BINANCE":
                if posicion['positionSide'] == "LONG":
                    if posicion['notional'] != "0":
                        size = float(posicion['positionAmt'])
                        avgPrice = float(posicion['entryPrice'])
                        #print("size long", size)
                        #print("")
        
        # Sumar todos los TP
        size_tp = 0
        for orden in ordenes_abiertas:
            
            if exchange == "BYBIT":
                if orden['reduceOnly'] and orden['positionIdx'] == 1:
                    size_tp = size_tp + float(orden['qty'])
            
            if exchange == "BINANCE":
                if orden['reduceOnly'] and orden['positionSide'] == "LONG":
                    size_tp = size_tp + float(orden['origQty'])
        #print("tps long", size_tp)
        #print("")

        # Comparar y equilibrar
        excedente = size - size_tp
        excedente = round(excedente-cantidad_usdt/precio_actual,decimales_moneda)
        #print("Excedente long de", excedente)
        #print("")
        if excedente > cantidad_usdt/precio_actual and precio_actual > 1.0027*avgPrice:
            if inverso:
                inverse.cerrar_posicion(exchange, activo, "long", size=excedente)
            else:
                future.cerrar_posicion(exchange, activo, "long", size=excedente)
                            
    # SHORT
        size = 0
        for posicion in posiciones:

            if exchange == "BYBIT":
                if posicion['positionIdx'] == 2:
                    if posicion['size'] != "0":
                        size = abs(float(posicion['size']))
                        avgPrice = float(posicion['avgPrice'])
                        #print("size short", size)
                        #print("")
            
            if exchange == "BINANCE":
                if posicion['positionSide'] == "SHORT":
                    if posicion['notional'] != "0":
                        size = abs(float(posicion['positionAmt']))
                        avgPrice = float(posicion['entryPrice'])
                        #print("size short", size)
                        #print("")
        
        # Sumar todos los TP
        size_tp = 0
        for orden in ordenes_abiertas:
            
            if exchange == "BYBIT":
                if orden['reduceOnly'] and orden['positionIdx'] == 2:
                    size_tp = size_tp + abs(float(orden['qty']))
            
            if exchange == "BINANCE":
                if orden['reduceOnly'] and orden['positionSide'] == "SHORT":
                    size_tp = size_tp + float(orden['origQty'])
        #print("tps short", size_tp)
        #print("")

        # Comparar y equilibrar
        excedente = size - size_tp
        excedente = round(excedente-cantidad_usdt_short/precio_actual,decimales_moneda)
        #print("Excedente short de", excedente)
        #print("")
        if excedente > cantidad_usdt_short/precio_actual and precio_actual < 0.9972*avgPrice:
            if inverso:
                inverse.cerrar_posicion(exchange, activo, "short", size=excedente)
            else:
                future.cerrar_posicion(exchange, activo, "short", size=excedente)
                    

    except Exception as e:
        print("ERROR EN LA FUNCIÓN equilibrio()")
        print(e)
        print("")
# -------------------------------------------------------

# Función auxiliar
#--------------------------------------------
def auxiliar():
    try:
        global precio_actual, ordenes_abiertas, posiciones, cuenta, apalancamiento, auto, parametros, grid, breakeven, parejas_compra_venta, parejas_compra_venta_short, pausa

        while iniciar_estrategia:

            ti = time.time()
            
            # Consultar precio actual
            if inverso:
                precio_actual = inverse_ws.precio_actual
                if precio_actual == 0:
                    precio_actual = inverse.precio_actual_activo(exchange=exchange, symbol=activo)
                    time.sleep(0.9)
            else:
                precio_actual = future_ws.precio_actual
                if precio_actual == 0:
                    precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)
                    time.sleep(0.9)
            
            # Obtener ordenes abiertas
            if inverso:
                ordenes_abiertas = inverse.obtener_ordenes(exchange, activo)
            else:
                ordenes_abiertas = future.obtener_ordenes(exchange, activo)

            # Obtener posiciones
            if inverso:
                posiciones = inverse.obtener_posicion(exchange, activo)
            else:
                posiciones = future.obtener_posicion(exchange, activo)

            # Patrimonio actual
            if inverso:
                cuenta = inverse.patrimonio(exchange=exchange,symbol=activo)*precio_actual
            else:
                cuenta = future.patrimonio(exchange=exchange)
            
            # Mantener margen
            margen()

            # Gestionar la dirección
            direccion()

            # Cambiar el apalancamiento
            if apalancamiento != float(posiciones[0]['leverage']):
                if inverso:
                    inverse.apalancamiento(exchange,activo,apalancamiento)
                else:
                    future.apalancamiento(exchange,activo,apalancamiento)
                apalancamiento = parametros['apalancamiento']
            
            if len(posiciones) == 2:
                if apalancamiento != float(posiciones[1]['leverage']):
                    if inverso:
                        inverse.apalancamiento(exchange,activo,apalancamiento)
                    else:
                        future.apalancamiento(exchange,activo,apalancamiento)
                    apalancamiento = parametros['apalancamiento']

            # Reiniciar las parejas
            if reiniciar_parejas:
                pausa = True
                parejas_compra_venta = []
                parejas_compra_venta_short = []
                parametros['reiniciar_parejas'] = False
                json.dump(parametros, open(parametros_copia, "w"), indent=4)
            
            # Equilibrar posiciones y take profits
            #equilibrio()

            if time.time()-ti > 9:
                print("Funciones auxialeres ejecutadas en:", round(time.time()-ti,2), "Segundos")
                print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN auxiliar()")
        print(e)
        print("")
#--------------------------------------------

# # FUNCIÓN QUE CALCULA LA ACUMULACIÓN DE ÓRDENES EN EL LIBRO DE ORDENES DE BINANCE
# -------------------------------------------------------------------------------
def order_book(symbol):
    try:
        from binance.client import Client
        import pygame
        from mutagen.mp3 import MP3
        from gtts import gTTS
        import time
        from datetime import datetime


        binance_client = Client(
                                    api_key="",
                                    api_secret="",
                                    tld="com"
                                )

        # Variables globales
        global libro

        # FUNCIÓN QUE GENERA UN ARCHIVO DE AUDIO A PARTIR DE UN TEXTO
        #------------------------------------------------------------
        def texto_audio(texto):
            try:
                # Variables globales
                global duracion

                # Eliminar la palabra "USDT"
                texto = texto.replace("USDT", "")
                
                # Elegir el idioma
                idioma = "es"
                
                #Escoger el tipo de voz
                voz = "female"
                
                # Indicar el texto, idioma y velocidad de lectura
                tts = gTTS(text=texto, lang=idioma, slow=False)
                
                # Generar el archivo de audio
                tts.save("future/estrategias/infinity/salida/alerta_voz.mp3")
                
                # Duracion del audio
                duracion = MP3("future/estrategias/infinity/salida/alerta_voz.mp3").info.length
            
            except Exception as e:
                print("ERROR EN LA FUNCIÓN QUE GENERA UN ARCHIVO DE AUDIO A PARTIR DE UN TEXTO. (texto_audio())")
                print(e)
                print("")
                tts = gTTS(text="ERROR", lang=idioma, slow=False)
                tts.save("alerta_voz.mp3")
        #------------------------------------------------------------

        # FUNCIÓN PARA REPRODUCIR SONIDOS
        #--------------------------------
        def reproducir_audio(audio):
            try:
                pygame.mixer.init()
                pygame.mixer.music.load(audio)
                pygame.mixer.music.play()
                time.sleep(duracion)
            except Exception as e:
                print("ERROR EN LA FUNCIÓN QUE REPRODUCE AUDIO")
                print(e)
        # -------------------------------

        # FUNCIÓN QUE ALERTA CUANDO UN ACTIVO ACUMULA CIERTA CANTIDAD DE ORDENES EN EL LIBRO DE ORDENES
        # ---------------------------------------------------------------------------------------------
        def alerta_ordenes(symbol, umbral):
            try:
                # Variables globales
                global precio, tiempo, libro, pausa

                # Definir el simbolo
                symbol = symbol.upper()
                
                if umbral != 0:
                
                    # ALCISTA
                    # Obtener las ordenes de compra
                    libro_compras = binance_client.futures_order_book(symbol=symbol, limit=1000)['bids']

                    # Decimales de la moneda
                    decimales_moneda = len((libro_compras[0][0]).split(".")[1])

                    # Sumar la cantidad de ordenes de compra
                    cantidad_compra = 0
                    for order in libro_compras:
                        cantidad_compra = cantidad_compra + float(order[1])
                   
                    # Emitir la alerta
                    if cantidad_compra*precio_actual > 1000000*umbral:
                        pausa = False
                        parametros['pausa'] = False
                        json.dump(parametros, open(parametros_copia, "w"), indent=4)
                        libro = "LONG"
                        precio = precio_actual
                        tiempo = time.time()
                        print("")
                        print("Acumulación de ordenes de compra")
                        print(f"{libro_compras[-1][0]} - {libro_compras[0][0]} ({round(float(libro_compras[0][0]) - float(libro_compras[-1][0]),decimales_moneda)})")
                        print(int(cantidad_compra), symbol.split("USDT")[0], ",", int(cantidad_compra*precio_actual), "USDT")
                        print(datetime.now().strftime('%Y-%m-%d - %I:%M:%S %p'))
                        print("")
                        texto_audio(f"Acumulación de órdenes de compra en {symbol.split('USDT')[0]}")
                        reproducir_audio("future/estrategias/infinity/salida/alerta_voz.mp3")

                    # BAJISTA
                    # Obtener las ordenes de venta
                    libro_ventas = binance_client.futures_order_book(symbol=symbol, limit=1000)['asks']

                    # Sumar la cantidad de ordenes de venta
                    cantidad_venta = 0
                    for order in libro_ventas:
                        cantidad_venta = cantidad_venta + float(order[1])

                    # Emitir la alerta
                    if cantidad_venta*precio_actual > 1000000*umbral:
                        pausa = False
                        parametros['pausa'] = False
                        json.dump(parametros, open(parametros_copia, "w"), indent=4)
                        libro = "SHORT"
                        precio = precio_actual
                        tiempo = time.time()
                        print("")
                        print("Acumulación de ordenes de venta")
                        print(f"{libro_ventas[0][0]} - {libro_ventas[-1][0]} ({round(float(libro_ventas[-1][0]) - float(libro_ventas[0][0]),decimales_moneda)})")
                        print(int(cantidad_venta), symbol.split("USDT")[0], ",", int(cantidad_venta*precio_actual), "USDT")
                        print(datetime.now().strftime('%Y-%m-%d - %I:%M:%S %p'))
                        print("")
                        texto_audio(f"Acumulación de órdenes de venta en {symbol.split('USDT')[0]}")
                        reproducir_audio("future/estrategias/infinity/salida/alerta_voz.mp3")
                
            except Exception as e:
                print("ERROR EN LA FUNCIÓN alerta_ordenes()")
                print(e)
                print("")
        # ---------------------------------------------------------------------------------------------

        print(f"Monitoreo del Order Book de {symbol}")
        print("")        
            

        porcentaje_distancia = 0.018 
        tiempo_espera = 9*60
        while True:

            ti = time.time()

            alerta_ordenes(symbol=symbol+"USDT",umbral=umbral)
            
            # Detener el libro
            if libro == "LONG":
                if precio_actual > (1+porcentaje_distancia)*precio or time.time()-tiempo > tiempo_espera:
                    libro = ""
            
            if libro == "SHORT":
                if precio_actual < (1-porcentaje_distancia)*precio or time.time()-tiempo > tiempo_espera:
                    libro = ""
            
            time.sleep(5.4)
            if time.time() - ti < retraso_api:
                time.sleep(retraso_api)

    except Exception as e:
        print("ERROR EN LA FUNCIÓN order_book()")
        print(e)
        print("")
# -------------------------------------------------------------------------------


# Inicializar posiciones y ordenes abiertas
# Obtener posiciones
if inverso:
    posiciones = inverse.obtener_posicion(exchange, activo)
else:
    posiciones = future.obtener_posicion(exchange, activo)
# Obtener ordenes abiertas
if inverso:
    ordenes_abiertas = inverse.obtener_ordenes(exchange, activo)
else:
    ordenes_abiertas = future.obtener_ordenes(exchange, activo)

# Cambiar el modo
if exchange == "BYBIT":
    if not(inverso) and posiciones[0]['positionIdx'] == 0:
        future.cambiar_modo(exchange,activo)

# Balance inicial
if inverso:
    balance_inicial = inverse.patrimonio(exchange=exchange,symbol=activo)
else:
    balance_inicial = future.patrimonio(exchange=exchange)

# Iniciar estrategia
iniciar_estrategia = False
pausa = False

# Consultar precio actual
if inverso:
    precio_actual = inverse.precio_actual_activo(exchange=exchange, symbol=activo)
else:
    precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)

# Margen disponible
if inverso:
    margen_disponible = future.margen_disponible(exchange)*apalancamiento*precio_actual
else:
    margen_disponible = future.margen_disponible(exchange)*apalancamiento
            
# Decimales del precio
decimales_precio = len(str(precio_actual).split(".")[-1])

# Decimales de la moneda
if precio_actual < 2:
    decimales_moneda = 0
if 2 < precio_actual < 100:
    decimales_moneda = 1
if 100 < precio_actual < 3600:
    decimales_moneda = 2
if 1000 < precio_actual < 9000:
    decimales_moneda = 3
if precio_actual > 5000:
    decimales_moneda = 4

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
riesgo_max = ganancia_actual()
beneficio_max = ganancia_actual()
mostrar_lista(parejas_compra_venta)
mostrar_lista(parejas_compra_venta_short)

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

# Iniciar estrategia
iniciar_estrategia = parametros()

# Iniciar hilo del precio actual
if inverso:
    hilo_precio_actual = threading.Thread(target=inverse_ws.precio_actual_activo, args=(exchange, activo))
    hilo_precio_actual.daemon = True
    hilo_precio_actual.start()
else:
    hilo_precio_actual = threading.Thread(target=future_ws.precio_actual_activo, args=(exchange, activo))
    hilo_precio_actual.daemon = True
    hilo_precio_actual.start()

# Consultar precio actual
if inverso:
    precio_actual = inverse_ws.precio_actual
    while precio_actual == None:
        precio_actual = inverse_ws.precio_actual
else:
    precio_actual = future_ws.precio_actual
    while precio_actual == None:
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
hilo_limpiar_parejas_long = threading.Thread(target=limpiar_parejas_long)
hilo_limpiar_parejas_long.daemon = True
hilo_limpiar_parejas_long.start()

# Iniciar Hilo que limpia las listas
hilo_limpiar_parejas_short = threading.Thread(target=limpiar_parejas_short)
hilo_limpiar_parejas_short.daemon = True
hilo_limpiar_parejas_short.start()

# Iniciar Hilo que imprime las parejas
hilo_imprimir_parejas = threading.Thread(target=imprimir_parejas)
hilo_imprimir_parejas.daemon = True
hilo_imprimir_parejas.start()

# Inicializar la tendencia
tendencia_detector = ["ALCISTA"]

# Iniciar Hilo que detecta la tendencia
hilo_detectar_tendencia = threading.Thread(target=detectar_tendencia, args=(exchange,activo))
hilo_detectar_tendencia.daemon = True
hilo_detectar_tendencia.start()

# Inicializar las variables del libro de ordenes
libro = ""
precio = 0
tiempo = 0

# Iniciar Hilo que monitorea el libro de ordenes de Binance
hilo_libro_ordenes = threading.Thread(target=order_book, args=(activo,))
hilo_libro_ordenes.daemon = True
hilo_libro_ordenes.start()

# Iniciar Hilo auxiliar
hilo_auxiliar = threading.Thread(target=auxiliar)
hilo_auxiliar.daemon = True
hilo_auxiliar.start()

while iniciar_estrategia:
    try:
        ti = time.time()

        # PARAMETROS DE LA ESTRATEGIA
        # ---------------------------
        try:
            parametros = json.load(open(parametros_copia, "r"))
        except Exception as e:
            print("ERROR LEYENDO PARAMETROS")
            print(e)
            print("")
        apalancamiento = float(parametros['apalancamiento'])
        precio_referencia = float(parametros['precio_referencia'])                            # Precio de referencia
        distancia_grid = float(parametros['distancia_grid'])+comision_grid                    # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
        tp = float(parametros['tp'])                                                          # Take profit para detener la estrategia por completo
        sl = float(parametros['sl'])                                                          # Stop Loss para detener la estrategia por completo
        tipo = parametros['direccion'].upper()                                                # LONG o SHORT. Si se deja en blanco opera en ambas direcciones
        pausa = parametros['pausa']
        ganancia_grid_long = float(parametros['ganancia_long'])                               # Ganancias por cada grid long
        ganancia_grid_short = float(parametros['ganancia_short'])                             # Ganancias por cada grid short
        invertir_ganancias_grid = parametros['invertir_ganancias_grid']
        condicional_long = parametros['condicional_long']                                     # Activar condicional de LONG
        condicional_short = parametros['condicional_short']                                   # Activar condicional de SHORT
        umbral = int(parametros['umbral_libro'])
        auto = parametros['auto']
        breakeven = parametros['descarga_breakeven']
        reiniciar_parejas = parametros['reiniciar_parejas']
        # ---------------------------
        
        # Calcular importes
        try:
            cantidad_usdt = cuenta*ganancia_grid_long/distancia_grid                              # Importe en USDT para cada long
            cantidad_usdt_short = cuenta*ganancia_grid_short/distancia_grid                       # Importe en USDT para cada short
        except Exception as e:
            print("ERROR CALCULANDO IMPORTES")
            print(e)
            print("")
            
        # Consultar precio actual
        if inverso:
            precio_actual = inverse_ws.precio_actual
            if precio_actual == None:
                precio_actual = inverse.precio_actual_activo(exchange=exchange, symbol=activo)
        else:
            precio_actual = future_ws.precio_actual
            if precio_actual == None:
                precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)

        # Verificar que el hilo detener_estrategia este activo
        if not(hilo_detener_estrategia.is_alive()):
            hilo_detener_estrategia = threading.Thread(target=detener_estrategia)
            hilo_detener_estrategia.daemon = True
            hilo_detener_estrategia.start()

        # Verificar que el hilo del precio actual este activo
        if inverso:
            if not(hilo_precio_actual.is_alive()):
                hilo_precio_actual = threading.Thread(target=inverse_ws.precio_actual_activo, args=(exchange, activo))
                hilo_precio_actual.daemon = True
                hilo_precio_actual.start()
        else:
            if not(hilo_precio_actual.is_alive()):
                hilo_precio_actual = threading.Thread(target=future_ws.precio_actual_activo, args=(exchange, activo))
                hilo_precio_actual.daemon = True
                hilo_precio_actual.start()

        # Verificar que el hilo actualizar grid este activo
        if not(hilo_actualizar_grid.is_alive()):
            hilo_actualizar_grid = threading.Thread(target=actualizar_grid)
            hilo_actualizar_grid.daemon = True
            hilo_actualizar_grid.start()

        # Verificar que el hilo limpiar parejas long este activo
        if not(hilo_limpiar_parejas_long.is_alive()):
            hilo_limpiar_parejas_long = threading.Thread(target=limpiar_parejas_long)
            hilo_limpiar_parejas_long.daemon = True
            hilo_limpiar_parejas_long.start()

        # Verificar que el hilo limpiar parejas short este activo
        if not(hilo_limpiar_parejas_short.is_alive()):
            hilo_limpiar_parejas_short = threading.Thread(target=limpiar_parejas_short)
            hilo_limpiar_parejas_short.daemon = True
            hilo_limpiar_parejas_short.start()

        # Verificar que el hilo imprimir parejas este activo
        if not(hilo_imprimir_parejas.is_alive()):
            hilo_imprimir_parejas = threading.Thread(target=imprimir_parejas)
            hilo_imprimir_parejas.daemon = True
            hilo_imprimir_parejas.start()

        # Verificar que el hilo detectar tendencia este activo
        if not(hilo_detectar_tendencia.is_alive()):
            hilo_detectar_tendencia = threading.Thread(target=detectar_tendencia, args=(exchange,activo))
            hilo_detectar_tendencia.daemon = True
            hilo_detectar_tendencia.start()

        # Verificar que el hilo libro ordenes este activo
        if not(hilo_libro_ordenes.is_alive()):
            hilo_libro_ordenes = threading.Thread(target=order_book, args=(activo,))
            hilo_libro_ordenes.daemon = True
            hilo_libro_ordenes.start()

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
    

        # Retraso por hiperactividad
        if time.time() - ti < retraso_api:
            time.sleep(retraso_api)

    except Exception as e:
        print("ERROR EN EL PROGRAMA PRINCIPAL")
        print(e)
        print("")

cerrar_todo()
mostrar_lista(parejas_compra_venta)
mostrar_lista(parejas_compra_venta_short)
cerrar_todo()