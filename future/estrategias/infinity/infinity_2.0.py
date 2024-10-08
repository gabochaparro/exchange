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
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import copy
import shutil
import os
import glob


# Especifica la ruta de la carpeta parametros
carpeta_parametros = 'future/estrategias/infinity/parametros/*'

# Usa glob para obtener todos los archivos dentro de la carpeta
archivos = glob.glob(carpeta_parametros)

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
fecha_inicio = int(time.time())
parametros = json.load(open("future/estrategias/infinity/parametros_infinity_2.0.json", "r"))       # Abrir el archivo parametros.json y cargar su contenido
parametros_copia = f"future/estrategias/infinity/parametros/{parametros['activo']}_{parametros['exchange']}_{fecha_inicio}.json"
shutil.copy("future/estrategias/infinity/parametros_infinity_2.0.json", parametros_copia)


# PARAMETROS DE LA ESTRATEGIA
# ---------------------------
parametros = json.load(open(parametros_copia, "r"))
exchange = parametros['exchange'].upper()                                                           # Exchange a utilizar
inverso = parametros['inverso']                                                                     # Futuros inversos (True/False)
activo = parametros['activo'].upper()                                                               # Activo a operar
apalancamiento = parametros['apalancamiento']                                                       # Se recomienda un apalancamiento muy bajo para esta estrategia (<=3x)
if inverso:
    inverse.apalancamiento(exchange,activo,apalancamiento)
else:
    future.apalancamiento(exchange,activo,apalancamiento)
precio_referencia = parametros['precio_referencia']                                                 # Precio de referencia
ganancia_grid = parametros['distancia_grid']+0.11                                                   # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
if inverso:
    cuenta = inverse.patrimonio(exchange=exchange,symbol=activo)  
else:
    cuenta = future.patrimonio(exchange=exchange)                                                   # Inversión de la estrategia
tp = float(parametros['tp'])                                                                        # Take profit para detener la estrategia por completo
sl = float(parametros['sl'])                                                                        # Stop Loss para detener la estrategia por completo
tipo = parametros['direccion'].upper()                                                              # LONG o SHORT. Si se deja en blanco opera en ambas direcciones
if inverso and exchange == "BYBIT":
    auto = False
else:
    auto = parametros['auto']
ganancia_grid_long = parametros['ganancia_long']                                               # Ganancias por cada grid long
ganancia_grid_short = parametros['ganancia_short']
cantidad_usdt = cuenta*ganancia_grid_long/parametros['distancia_grid']                              # Importe en USDT para cada compra del long
cantidad_usdt_short = cuenta*ganancia_grid_short/parametros['distancia_grid']                       # Importe en USDT para cada compra del short
condicional_long = parametros['condicional_long']                                                   # Activar condicional de LONG
condicional_short = parametros['condicional_short']                                                 # Activar condicional de SHORT
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

            # LONG
            while grid[-1] <= precio_actual != 0:
                
                # Agregar un nuevo nivel al grid
                nuevo_nivel = round(grid[-1]*(1+ganancia_grid/100),decimales_precio)
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
                nuevo_nivel = round(grid[0]/(1+ganancia_grid/100),decimales_precio)
                if nuevo_nivel not in grid:
                    grid.insert(0,nuevo_nivel)
                
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
        if inverso:
            cantidad_monedas = round(cantidad_usdt)
            cantidad_monedas_short = round(cantidad_usdt_short)
        else:
            cantidad_monedas = round((cantidad_usdt/precio_actual),decimales_moneda)
            cantidad_monedas_short = round((cantidad_usdt_short/precio_actual),decimales_moneda)
        
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
        
        # Recorrer el grid y encontrar el próximo precio de compra y venta
        prox_compra = 0
        prox_venta = 0
        while prox_compra == 0 or prox_venta == 0:
            for grilla in grid:
                if grilla <= precio_actual < grilla*(1+ganancia_grid/100):
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
        
        for pareja in parejas_compra_venta:
            if historial_ordenes != None:
                
                # Obtener la orden de compra
                for orden in historial_ordenes:
                    
                    # Obtener la orden de compra
                    if orden['orderId'] == pareja['compra']['orderId']:
                
                        # BYBIT
                        if exchange.upper() == "BYBIT":

                            # Obtener la orden de compra en Bybit
                            if orden['orderStatus'] == "Filled" and pareja['compra']['ejecutada'] == False:
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['compra']['cantidad'] = float(orden['qty'])
                                pareja['compra']['price'] = round(float(orden['avgPrice']),decimales_precio)
                                pareja['compra']['monto'] = pareja['compra']['cantidad']*pareja['compra']['price']
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                break
                                
                        # BINANCE
                        if exchange.upper() == "BINANCE":

                            # Obtener la orden de compra en Binance
                            if orden['status'] == "FILLED" and pareja['compra']['ejecutada'] == False:
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['compra']['cantidad'] = float(orden['qty'])
                                pareja['compra']['price'] = round(float(orden['avgPrice']),decimales_precio)
                                pareja['compra']['monto'] = pareja['compra']['cantidad']*pareja['compra']['price']
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                break
                
                # Obtener la orden de venta
                for orden in historial_ordenes:
                    
                    # Obtener la orden de venta
                    if orden['orderId'] == pareja['venta']['orderId']:
                        
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                    
                            # Obtener la orden de venta en Bybit
                            if orden['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = float(orden['qty'])
                                pareja['venta']['price'] = round(float(orden['avgPrice']),decimales_precio)
                                pareja['venta']['monto'] = pareja['venta']['cantidad']*pareja['venta']['price']
                                pareja['general']['beneficios'] = 0.9989*(pareja['venta']['monto']-pareja['compra']['monto'])
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                
                                # Cancelar la orden de SL en caso tenga
                                if pareja['sl']['orderId'] != "":
                                    if inverso:
                                        inverse.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                    else:
                                        future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                
                                break
                                
                        # BINANCE
                        if exchange.upper() == "BINANCE":
                    
                            # Obtener la orden de venta en Binance
                            if orden['status'] == "FILLED" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = float(orden['qty'])
                                pareja['venta']['price'] = round(float(orden['avgPrice']),decimales_precio)
                                pareja['venta']['monto'] = pareja['venta']['cantidad']*pareja['venta']['price']
                                pareja['general']['beneficios'] = 0.9989*(pareja['venta']['monto']-pareja['compra']['monto'])
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                
                                # Cancelar la orden de SL en caso tenga
                                if pareja['sl']['orderId'] != "":
                                    if inverso:
                                        inverse.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                    else:
                                        future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                
                                break
                            
                    # Obtener la orden de sl
                    if pareja['sl']['orderId'] != "":
                        if inverso:
                            ordenes_sl = inverse.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['sl']['orderId'])
                        else:
                            ordenes_sl = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['sl']['orderId'])
                        
                        if ordenes_sl != None and ordenes_sl != []:
                            if exchange == "BYBIT":
                                if ordenes_sl[0]['orderStatus'] == "Filled":
                                    
                                    # Cancelar la orden venta en caso se haya tocado el SL
                                    if pareja['venta']['orderId'] != "":
                                        if inverso:
                                            inverse.cancelar_orden(exchange, activo, orderId=pareja['venta']['orderId'])
                                        else:
                                            future.cancelar_orden(exchange, activo, orderId=pareja['venta']['orderId'])
                                        print("TP Cancelado.")
                                        print("")
                                        parejas_compra_venta.remove(pareja)
                                        print("Pareja removida.", pareja)
                                        print("")
                        break

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
                            
                            # Obtener la orden de compra en BYBIT
                                if orden['orderStatus'] == "Filled" and not(pareja['compra']['ejecutada']):
                                    pareja['compra']['ejecutada'] = True
                                    pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                    pareja['compra']['cantidad'] = float(orden['qty'])
                                    pareja['compra']['price'] = round(float(orden['avgPrice']),decimales_precio)
                                    pareja['compra']['monto'] = pareja['compra']['cantidad']*pareja['compra']['price']
                                    pareja['general']['beneficios'] = 0.9989*(pareja['venta']['monto']-pareja['compra']['monto'])
                                    #print(json.dumps(parejas_compra_venta_short,indent=2))
                                        
                                    # Cancelar la orden de SL en caso tenga
                                    if pareja['sl']['orderId'] != "":
                                        if inverso:
                                            inverse.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        else:
                                            future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                        print("SL Cancelado.")
                                    
                                    break
                                
                        # BINANCE
                        if exchange.upper() == "BINANCE":

                            # Obtener la orden de compra en Binance
                            if orden['status'] == "FILLED" and pareja['compra']['ejecutada'] == False:
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['compra']['cantidad'] = float(orden['qty'])
                                pareja['compra']['price'] = round(float(orden['avgPrice']),decimales_precio)
                                pareja['compra']['monto'] = pareja['compra']['cantidad']*pareja['compra']['price']
                                pareja['general']['beneficios'] = 0.9989*(pareja['venta']['monto']-pareja['compra']['monto'])
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                        
                                # Cancelar la orden de SL en caso tenga
                                if pareja['sl']['orderId'] != "":
                                    if inverso:
                                        inverse.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                    else:
                                        future.cancelar_orden(exchange, activo, orderId=pareja['sl']['orderId'])
                                    print("SL Cancelado.")
                                
                                break
                
                # Obtener la orden de venta
                for orden in historial_ordenes:
                        
                    # Obtener la orden de Venta
                    if orden['orderId'] == pareja['venta']['orderId']:
                
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                            
                            # Obtener la orden de venta en BYBIT
                            if orden['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = float(orden['qty'])
                                pareja['venta']['price'] = round(float(orden['avgPrice']),decimales_precio)
                                pareja['venta']['monto'] = pareja['venta']['cantidad']*pareja['venta']['price']
                                #print(json.dumps(parejas_compra_venta_short,indent=2))
                                
                                break
                                
                        # BINANCE
                        if exchange.upper() == "BINANCE":
                    
                            # Obtener la orden de venta en Binance
                            if orden['status'] == "FILLED" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = float(orden['qty'])
                                pareja['venta']['price'] = round(float(orden['avgPrice']),decimales_precio)
                                pareja['venta']['monto'] = pareja['venta']['cantidad']*pareja['venta']['price']
                                #print(json.dumps(parejas_compra_venta,indent=2))
                                
                                break
                            
                    # Obtener la orden de sl en BYBIT
                    if pareja['sl']['orderId'] != "":
                        if inverso:
                            ordenes_sl = inverse.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['sl']['orderId'])
                        else:
                            ordenes_sl = future.obtener_ordenes(exchange=exchange, symbol=symbol, orderId=pareja['sl']['orderId'])
                        
                        if ordenes_sl != None and ordenes_sl != []:
                            if exchange == "BYBIT":
                                if ordenes_sl[0]['orderStatus'] == "Filled":
                                    
                                    # Cancelar la orden compra en caso se haya tocado el SL
                                    if pareja['compra']['orderId'] != "":
                                        if inverso:
                                            inverse.cancelar_orden(exchange, activo, orderId=pareja['compra']['orderId'])
                                        else:
                                            future.cancelar_orden(exchange, activo, orderId=pareja['compra']['orderId'])
                                        print("TP Cancelado.")
                                        print("")
                                        parejas_compra_venta.remove(pareja)
                                        print("Pareja removida.", pareja)
                                        print("")

        #print("Parejas short actualizadas", time.time()-ti, "segundos")
    
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
        global parejas_compra_venta, parejas_compra_venta_short
        
        while iniciar_estrategia:
            if parejas_compra_venta != [] or parejas_compra_venta_short != []:

                ti = time.time()
                
                # Obtener tamaño de la posición long
                if inverso:
                    posiciones = inverse.obtener_posicion(exchange, activo)
                else:
                    posiciones = future.obtener_posicion(exchange, activo)
                
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

                # Obtener ordenes abiertas
                if inverso:
                    ordenes_abiertas = inverse.obtener_ordenes(exchange, activo)
                else:
                    ordenes_abiertas = future.obtener_ordenes(exchange, activo)

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
                        
                        if ordenes_abiertas != []:
                            
                            orden_puesta = False
                            for orden in ordenes_abiertas:
                                
                                # Verificar si hay una orden limite
                                if 0.999*pareja['compra']['price'] <= float(orden['price']) <= 1.001*pareja['compra']['price'] and orden['side'].upper() == "BUY" and not(orden['reduceOnly']):
                                    orden_puesta = True
                                
                                if exchange == "BYBIT":
                                    # Verificar si hay una orden condicional
                                    if orden['triggerPrice'] != "":
                                        if 0.999*pareja['compra']['price'] <= float(orden['triggerPrice']) <= 1.001*pareja['compra']['price'] and orden['side'].upper() == "BUY" and not(orden['reduceOnly']) :
                                            orden_puesta = True
                                
                                if exchange == "BINANCE":
                                    # Verificar si hay una orden condicional
                                    if orden['stopPrice'] != "":
                                        if 0.999*pareja['compra']['price'] <= float(orden['stopPrice']) <= 1.001*pareja['compra']['price'] and orden['side'] == "BUY" and not(orden['reduceOnly']) :
                                            orden_puesta = True
                            
                            if not(orden_puesta):
                                actualizar_pareja_long(exchange=exchange, symbol=activo)
                                if not(pareja['compra']['ejecutada']):
                                    if pareja in parejas_compra_venta:
                                        parejas_compra_venta.remove(pareja)
                                        print("Pareja long removida!", pareja)
                                        print("")
                                        
                
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
        global parejas_compra_venta, parejas_compra_venta_short
        
        while iniciar_estrategia:
            if parejas_compra_venta != [] or parejas_compra_venta_short != []:

                ti = time.time()
                
                # Obtener tamaño de la posición short
                if inverso:
                    posiciones = inverse.obtener_posicion(exchange, activo)
                else:
                    posiciones = future.obtener_posicion(exchange, activo)
                
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
                if inverso:
                    ordenes_abiertas = inverse.obtener_ordenes(exchange, activo)
                else:
                    ordenes_abiertas = future.obtener_ordenes(exchange, activo)

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
                        
                        if ordenes_abiertas != []:
                            
                            # Verificar si estan puestas las ordenes
                            orden_puesta = False
                            for orden in ordenes_abiertas:
                                
                                # Verificar si hay una orden limite
                                if 0.999*pareja['venta']['price'] <= float(orden['price']) <= 1.001*pareja['venta']['price'] and orden['side'].upper() == "SELL" and not(orden['reduceOnly']):
                                    orden_puesta = True
                                
                                
                                # Verificar si hay una orden condicional
                                if exchange == "BYBIT":
                                    if orden['triggerPrice'] != "":
                                        if 0.999*pareja['venta']['price'] <= float(orden['triggerPrice']) <= 1.001*pareja['venta']['price'] and orden['side'].upper() == "SELL" and not(orden['reduceOnly']):
                                            orden_puesta = True
                                
                                if exchange == "BINANCE":
                                    if orden['stopPrice'] != "":
                                        if 0.999*pareja['venta']['price'] <= float(orden['stopPrice']) <= 1.001*pareja['venta']['price'] and orden['side'] == "SELL" and not(orden['reduceOnly']):
                                            orden_puesta = True
                            
                            if not(orden_puesta):
                                actualizar_pareja_short(exchange=exchange, symbol=activo)
                                if not(pareja['venta']['ejecutada']):
                                    if pareja in parejas_compra_venta_short:
                                        parejas_compra_venta_short.remove(pareja)
                                        print("Pareja short removida!", pareja)
                                        print("")
                
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
        nueva_compra = 0
        nueva_venta = 0
        while iniciar_estrategia:

            if tipo == "" or tipo == "LONG":
                
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
                        if 0.999*pareja["compra"]['price'] < prox_compra < 1.001*pareja["compra"]['price']:
                            orden_compra_puesta = True
                            
                        # Verificar la orden condicional
                        if 0.999*pareja["compra"]['price'] < prox_venta < 1.001*pareja["compra"]['price']:
                            orden_condicional_compra_puesta = True
                
                # Cantidad de cada compra
                if inverso:
                    qty = round(cantidad_usdt)
                else:
                    qty = round((cantidad_usdt/precio_actual),decimales_moneda)
                
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                orden_compra = None
                
                # Colocar la orden limite de compra y crear la pareja de compra_veta
                if not(orden_compra_puesta):
                    if margen_disponible > cantidad_usdt > 5.4 and precio_actual > prox_compra:
                        if inverso:
                            orden_compra = inverse.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_compra, side="BUY", leverage=apalancamiento)
                        else:
                            orden_compra = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_compra, side="BUY", leverage=apalancamiento)
                        if orden_compra != None:
                            parejas_compra_venta.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": 0
                                                                    },
                                                        "compra": {
                                                                    "orderId": orden_compra['orderId'],
                                                                    "price": orden_compra['price'],
                                                                    "cantidad": orden_compra['qty'],
                                                                    "monto": orden_compra['qty']*orden_compra['price'],
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": "",
                                                                    "price": prox_venta,
                                                                    "cantidad": orden_compra['qty'],
                                                                    "monto": orden_compra['qty']*prox_venta,
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
                    if margen_disponible > cantidad_usdt > 5.4 and precio_actual < prox_venta:
                        if inverso:
                            orden_compra = inverse.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_venta, side="BUY", leverage=apalancamiento)
                        else:
                            orden_compra = future.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_venta, side="BUY", leverage=apalancamiento)
                        if orden_compra != None:
                            parejas_compra_venta.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": 0
                                                                    },
                                                        "compra": {
                                                                    "orderId": orden_compra['orderId'],
                                                                    "price": orden_compra['price'],
                                                                    "cantidad": orden_compra['qty'],
                                                                    "monto": orden_compra['qty']*orden_compra['price'],
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": "",
                                                                    "price": round(prox_venta*(1+ganancia_grid/100),decimales_precio),
                                                                    "cantidad": orden_compra['qty'],
                                                                    "monto": orden_compra['qty']*round(prox_venta*(1+ganancia_grid/100),decimales_precio),
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
            
            # Colocar la orden de compra
            for compra_venta in parejas_compra_venta:
                if compra_venta["compra"]['ejecutada'] and compra_venta["venta"]['orderId'] == "":
                        
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
                    
                    if size != "0":
                        
                        # Colocar TP
                        orden = None
                        if precio_actual < compra_venta["venta"]['price']: #> 1.0011*avgPrice:
                            if inverso:
                                orden = inverse.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["venta"]['price'], type="LIMIT",tpSize=str(compra_venta["venta"]['cantidad']))
                            else:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="LONG", stopPrice=compra_venta["venta"]['price'], type="LIMIT",tpSize=str(compra_venta["venta"]['cantidad']))
                        if precio_actual > compra_venta["venta"]['price']: #> 1.0011*avgPrice:
                            if inverso:
                                orden = inverse.cerrar_posicion(exchange, activo, "long", size=str(compra_venta["venta"]['cantidad']))['result']
                            else:
                                orden = future.cerrar_posicion(exchange, activo, "long", size=str(compra_venta["venta"]['cantidad']))['result']
                        
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
                        
                        # Verificar que la respuesta sea válida antes de modificar la pareja
                        if orden != None:
                            compra_venta["venta"]['orderId'] = orden['orderId']
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            print("")
                            #print(json.dumps(parejas_compra_venta,indent=2))

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

            if tipo == "" or tipo == "SHORT":
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
                            if 0.999*pareja["venta"]['price'] < prox_venta < 1.001*pareja["venta"]['price']:
                                orden_venta_puesta = True
                                
                            # Verificar orden condicional
                            if 0.999*pareja["venta"]['price'] < prox_compra < 1.001*pareja["venta"]['price']:
                                orden_condicional_venta_puesta = True
                
                # Cantidad de cada compra
                qty = round((cantidad_usdt_short/precio_actual),decimales_moneda)
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                orden_venta = None
                
                # Colocar la orden limite de compra y crear la pareja de compra_veta
                if not(orden_venta_puesta):
                    if margen_disponible > cantidad_usdt_short > 5.4 and precio_actual < prox_venta:
                        if inverso:
                            orden_venta = inverse.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_venta, side="SELL", leverage=apalancamiento)
                        else:
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
                                                                    "cantidad": orden_venta['qty'],
                                                                    "monto": orden_venta['qty']*prox_compra,
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": orden_venta['orderId'],
                                                                    "price": orden_venta['price'],
                                                                    "cantidad": orden_venta['qty'],
                                                                    "monto": orden_venta['qty']*orden_venta['price'],
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
                    if margen_disponible > cantidad_usdt_short > 5.4 and precio_actual > prox_compra:
                        if inverso:
                            orden_venta = inverse.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_compra, side="SELL", leverage=apalancamiento)
                        else:
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
                                                                    "cantidad": orden_venta['qty'],
                                                                    "monto": orden_venta['qty']*round(prox_compra/(1+ganancia_grid/100),decimales_precio),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "venta": {
                                                                    "orderId": orden_venta['orderId'],
                                                                    "price": orden_venta['price'],
                                                                    "cantidad": orden_venta['qty'],
                                                                    "monto": orden_venta['qty']*orden_venta['price'],
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

# Funció que coloca lsa ordenes de compra para SHORT
# --------------------------------------------------
def ordenes_compra_short(exchange, symbol):
    try:
        while iniciar_estrategia:
            
            # Colocar la orden de compra y actualiza la pareja de compra_veta
            for compra_venta in parejas_compra_venta_short:
                if compra_venta["venta"]['ejecutada'] and compra_venta["compra"]['orderId'] == "":
                            
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
                        orden = None
                        if precio_actual > compra_venta["compra"]['price']: #< 0.999*avgPrice:
                            if inverso:
                                orden = inverse.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=compra_venta["compra"]['price'], type="LIMIT",tpSize=str(compra_venta["compra"]['cantidad']))
                            else:
                                orden = future.take_profit(exchange=exchange, symbol=symbol, positionSide="SHORT", stopPrice=compra_venta["compra"]['price'], type="LIMIT",tpSize=str(compra_venta["compra"]['cantidad']))
                        if precio_actual < compra_venta["compra"]['price']: #< 0.999*avgPrice:
                            if inverso:
                                orden = inverse.cerrar_posicion(exchange, activo, "short", size=str(compra_venta["compra"]['cantidad']))['result']
                            else:
                                orden = future.cerrar_posicion(exchange, activo, "short", size=str(compra_venta["compra"]['cantidad']))['result']
                            
                        # Verificar que la respuesta sea válida antes de modificar la pareja
                        if orden != None:
                            compra_venta["compra"]['orderId'] = orden['orderId']
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            print("")
                            #print(json.dumps(parejas_compra_venta_short,indent=2))

    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_venta()")
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
            margen_disponible = inverse.margen_disponible(exchange,activo)*apalancamiento
        else:
            margen_disponible = future.margen_disponible(exchange)*apalancamiento
        
            
        # LONG
        if tipo == "" or "LONG":
            if margen_disponible < cantidad_usdt:
                
                max_distancia = 0
                pendiente = 0
                for pareja in parejas_compra_venta:
                    
                    # Buscar le mas bajo
                    if not(pareja['compra']['ejecutada']) and abs(pareja['compra']['price']-precio_actual) > max_distancia:
                        max_distancia = abs(pareja['compra']['price']-precio_actual)
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
                    parejas_compra_venta.remove(pareja_eliminar)
            
        # SHORT
        if tipo == "" or "SHORT":
            if margen_disponible < cantidad_usdt_short:
                
                max_distancia = 0
                pendiente = 0
                for pareja in parejas_compra_venta_short:
                    
                    # Buscar le mas alto
                    if not(pareja['venta']['ejecutada']) and abs(pareja['venta']['price']-precio_actual) > max_distancia:
                        max_distancia = abs(pareja['venta']['price']-precio_actual)
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

        # Crear una imagen en blanco
        img_width, img_height = 360, 300*(len(data)+1)
        background_color = (35, 35, 40)
        text_color = (200, 200, 200)
        greenlight_color = (0, 255, 0)
        redlight_color = (255, 0, 0)
        image = Image.new('RGB', (img_width, img_height), color=background_color)

        # Configurar el objeto de dibujo y la fuente
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()  # Puedes cambiar esto por una fuente específica si lo deseas

        # Dibujar los datos en la imagen
        if inverso:
            draw.text((10, 10), f" - INFINITY  Future Inverso - {activo.upper()} - {datetime.now().strftime('%Y-%m-%d - %I:%M:%S %p')} -", font=font, fill=text_color)
        else:
            draw.text((10, 10), f" - INFINITY  Future - {activo.upper()} - {datetime.now().strftime('%Y-%m-%d - %I:%M:%S %p')} -", font=font, fill=text_color)
        draw.text((10, 30), f"Balance inicial:", font=font, fill=text_color)
        draw.text((180, 30), f"{round(balance_inicial,2)} USDT", font=font, fill=text_color)
        draw.text((10, 50), f"Balance actual:", font=font, fill=text_color)
        if inverso:
            draw.text((180, 50), f"{round(inverse.patrimonio(exchange,activo),2)} USDT", font=font, fill=text_color)
        else:
            draw.text((180, 50), f"{round(future.patrimonio(exchange),2)} USDT", font=font, fill=text_color)
        
        ganancias_grid = 0
        parejas_completadas = 0
        if data != []:
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
        draw.text((180, 90), f"{round(balance_inicial*ganancia/100,3)} USDT ({round(ganancia,2)}%) ({round(riesgo_max,2)}%)", font=font, fill=color_ganancias)

        if data != []:
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
            image.save(f'future/estrategias/infinity/salida/{activo}_{exchange}_{fecha_inicio}_long.png')
        if data == parejas_compra_venta_short:
            image.save(f'future/estrategias/infinity/salida/{activo}_{exchange}_{fecha_inicio}_short.png')

        # Mostrar la imagen
        #image.show()

        tf = time.time()
        if tf-ti > 5.4:
            print(f"Parejas mostradas en {tf-ti} Segundos")
            print("")

    except Exception as e:
        print("ERROR EN LA FUNCIÓN mostrar_lista()")
        print(e)
        print("")
# -----------------------------------------------------

# Funciôn que gestiona la impresión de las parejas
# ------------------------------------------------
def imprimir_parejas():
    try:
        parejas_long = copy.deepcopy(parejas_compra_venta)
        parejas_short = copy.deepcopy(parejas_compra_venta_short)
        
        while iniciar_estrategia:

            # Mostrar parejas Long
            if parejas_compra_venta != parejas_long:
                parejas_long = parejas_compra_venta.copy()
                mostrar_lista(parejas_compra_venta)
            
            # Mostrar parejas Short
            if parejas_compra_venta_short != parejas_short:
                parejas_short = parejas_compra_venta_short.copy()
                mostrar_lista(parejas_compra_venta_short)

    except Exception as e:
        print("ERROR EN LA FUNCIÓN imprimir_parejas()")
# ------------------------------------------------

# Función que mide la ganancia actual (en porcentaje %)
# -----------------------------------------------------
def ganancia_actual():
    try:
        
        # Obtener posiciones
        if inverso:
            posiciones = inverse.obtener_posicion(exchange, activo)
        else:
            posiciones = future.obtener_posicion(exchange, activo)
        size = 0
        for posicion in posiciones:
            if exchange == "BYBIT":
                if posicion['positionIdx'] == 0:
                    size = size + float(posicion['size'])
                if posicion['positionIdx'] == 1:
                    size = size + float(posicion['size'])
                if posicion['positionIdx'] == 2:
                    size = size + float(posicion['size'])
        
        if inverso:
            return 100*((inverse.patrimonio(exchange,activo)-size*0.001) - balance_inicial)/balance_inicial
        else:
            return 100*((future.patrimonio(exchange)-size*precio_actual*0.001) - balance_inicial)/balance_inicial

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
        global iniciar_estrategia, riesgo_max

        # Riesgo máximo alcanzado
        riesgo_actual = ganancia_actual()
        if 0 > riesgo_actual < riesgo_max:
            riesgo_max = riesgo_actual

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
        if ((ganancia_actual() > tp and 100*(ganancias_grid+ganancias_grid_short)/balance_inicial > tp) or ganancia_actual() > tp) and tp > 0:
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
                print("ERROR EN LA FUNCIÓN. obtener_velas_precio()")
                print(e)
                print("")
                velas = []
                return velas
        #---------------------------------------------------------------------------------------
        
        # FUNCIÓN QUE BUSCA LA SERIE DE VELAS
        # -----------------------------------
        def serie_velas():
            try:
                global serie
                lista_velas = []
                for intervalo in intervalos:
                    lista_velas.append(obtener_velas_precio(symbol,intervalo))
                
                serie = lista_velas
                #print("Nueva Serie de Velas")
                time.sleep(60)
            except Exception as e:
                print("ERROR EN LA FUNCIÓN velas()")
                print(e)
                print("")
        # -----------------------------------

        # FUNCIÓN QUE DETERMINA LA TENDENCIA SEGÚN LAS VELAS
        # --------------------------------------------------
        def tendencia(velas):
            try:
                # Incializar variables
                velas = velas
                vela_inicial_apertura = float(velas[0][1])
                vela_medio_apertura = float(velas[1][1])
                vela_medio_cierre = float(velas[1][4])
                vela_final_cierre = future_ws.precio_actual
                
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

        serie_velas()
        hilo_serie = threading.Thread(target=serie_velas)
        hilo_serie.daemon = True
        hilo_serie.start()
        
        while iniciar_estrategia:
            if not(hilo_serie.is_alive()):
                hilo_serie = threading.Thread(target=serie_velas)
                hilo_serie.daemon = True
                hilo_serie.start()
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
        
        # Cambiar la dirección a LONG
        if tendencia_detector[0] == "ALCISTA":
            if tipo != "LONG":
                if auto:
                    print("Cambio de tendencia!", tendencia_detector[0])
                    print("")
                    parametros['direccion'] = "LONG"
                    json.dump(parametros, open(parametros_copia, "w"), indent=4)
            
        # Cambiar la dirección a SHORT
        if tendencia_detector[0] == "BAJISTA":
            if tipo != "SHORT":
                if auto:
                    print("Cambio de tendencia!", tendencia_detector[0])
                    print("")
                    parametros['direccion'] = "SHORT"
                    json.dump(parametros, open(parametros_copia, "w"), indent=4)
            
        # Cambiar la dirección a RANGO
        if tendencia_detector[0] == "RANGO":
            if tipo != "":
                if auto:
                    print("Cambio de tendencia!", tendencia_detector[0])
                    print("")
                    parametros['direccion'] = ""
                    json.dump(parametros, open(parametros_copia, "w"), indent=4)

        if tipo == "LONG":
            # Cancelar todas las ordenes short
            for orden in ordenes_abiertas:  
                for pareja in parejas_compra_venta_short:
                    if exchange == "BYBIT":
                        if orden['positionIdx'] == 2 and not(orden['reduceOnly']) and orden['orderId'] == pareja['venta']['orderId']:
                            if inverso:
                                inverse.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                            else:
                                future.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                            if pareja in parejas_compra_venta_short:
                                parejas_compra_venta_short.remove(pareja)

        if tipo == "SHORT":
            # Cancelar todas las ordenes long
            for orden in ordenes_abiertas:
                for pareja in parejas_compra_venta:
                    if exchange == "BYBIT":
                        if orden['positionIdx'] == 1 and not(orden['reduceOnly']) and orden['orderId'] == pareja['compra']['orderId']:
                            if inverso:
                                inverse.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                            else:
                                future.cancelar_orden(exchange, activo, orderId=orden['orderId'])
                            if pareja in parejas_compra_venta:
                                parejas_compra_venta.remove(pareja)
    
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
        
        # Sumar todos los TP
        size_tp = 0
        for orden in ordenes_abiertas:
            
            if exchange == "BYBIT":
                if orden['reduceOnly'] and orden['positionIdx'] == 1:
                    size_tp = size_tp + float(orden['qty'])
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
        
        # Sumar todos los TP
        size_tp = 0
        for orden in ordenes_abiertas:
            
            if exchange == "BYBIT":
                if orden['reduceOnly'] and orden['positionIdx'] == 2:
                    size_tp = size_tp + abs(float(orden['qty']))
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
        global precio_actual, ordenes_abiertas, cuenta
        
        while iniciar_estrategia:

            ti = time.time()
            
            # Consultar precio actual
            if inverso:
                precio_actual = inverse_ws.precio_actual
            else:
                precio_actual = future_ws.precio_actual
            
            # Obtener ordenes abiertas
            if inverso:
                ordenes_abiertas = inverse.obtener_ordenes(exchange, activo)
            else:
                ordenes_abiertas = future.obtener_ordenes(exchange, activo)

            # Mantener margen
            margen()

            # Gestionar la  dirección
            direccion()

            # Equilibrar posiciones y take profits
            #equilibrio()

            # Patrimonio actual
            if inverso:
                cuenta = inverse.patrimonio(exchange=exchange,symbol=activo)
            else:
                cuenta = future.patrimonio(exchange=exchange)

            if time.time()-ti > 9:
                print("Funciones auxialeres ejecutadas en:", round(time.time()-ti,2), "Segundos")
                print("")
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN auxiliar()")
        print(e)
        print("")
#--------------------------------------------

# Balance inicial
balance_inicial = cuenta

# Iniciar estrategia
iniciar_estrategia = False

# Consultar precio actual
if inverso:
    precio_actual = inverse.precio_actual_activo(exchange=exchange, symbol=activo)
else:
    precio_actual = future.precio_actual_activo(exchange=exchange, symbol=activo)

# Margen disponible
if inverso:
    margen_disponible = future.margen_disponible(exchange)*apalancamiento
else:
    margen_disponible = future.margen_disponible(exchange)*apalancamiento
            
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
riesgo_max = ganancia_actual()
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

# Cantidad de cada compra en USDT
cantidad_usdt, cantidad_usdt_short = parametros()

# Iniciar estrategia
iniciar_estrategia = True

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
    while precio_actual == 0:
        precio_actual = inverse_ws.precio_actual
else:
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

# Iniciar Hilo auxiliar
hilo_auxiliar = threading.Thread(target=auxiliar)
hilo_auxiliar.daemon = True
hilo_auxiliar.start()

while iniciar_estrategia:
    try:

        # PARAMETROS DE LA ESTRATEGIA
        # ---------------------------
        parametros = json.load(open(parametros_copia, "r"))                                                 # Abrir el archivo parametros.json y cargar su contenido
        if apalancamiento != parametros['apalancamiento']:
            apalancamiento = parametros['apalancamiento']                                                           # Se recomienda un apalancamiento muy bajo para esta estrategia (<=3x)
            if inverso:
                inverse.apalancamiento(exchange,activo,apalancamiento)
            else:
                future.apalancamiento(exchange,activo,apalancamiento)
        precio_referencia = parametros['precio_referencia']                                                 # Precio de referencia
        ganancia_grid = parametros['distancia_grid']+0.11                                                   # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
        tp = float(parametros['tp'])                                                                        # Take profit para detener la estrategia por completo
        sl = float(parametros['sl'])                                                                        # Stop Loss para detener la estrategia por completo
        tipo = parametros['direccion'].upper()                                                              # LONG o SHORT. Si se deja en blanco opera en ambas direcciones
        if inverso and exchange == "BYBIT":
            auto = False
        else:
            auto = parametros['auto']
        ganancia_grid_long = parametros['ganancia_long']                                               # Ganancias por cada grid long
        ganancia_grid_short = parametros['ganancia_short']                                                # Ganancias por cada grid short
        cantidad_usdt = cuenta*ganancia_grid_long/parametros['distancia_grid']                              # Importe en USDT para cada compra del long
        cantidad_usdt_short = cuenta*ganancia_grid_short/parametros['distancia_grid']                       # Importe en USDT para cada compra del short
        condicional_long = parametros['condicional_long']                                                   # Activar condicional de LONG
        condicional_short = parametros['condicional_short']                                                 # Activar condicional de SHORT
        # ---------------------------
            
        # Consultar precio actual
        if inverso:
            precio_actual = inverse_ws.precio_actual
        else:
            precio_actual = future_ws.precio_actual

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
            if not(hilo_precio_actual.is_alive()) or future_ws.precio_actual == 0:
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
        print(e)
        print("")

cerrar_todo()
mostrar_lista(parejas_compra_venta)
mostrar_lista(parejas_compra_venta_short)
cerrar_todo()
