''' 
Grid de spot que imita el comportamiento del grid spot infinity de BingX.
'''
import spot
import spot_ws
import json
import time
import threading
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime



# PARAMETROS DE LA ESTRATEGIA
# ---------------------------
parametros = json.load(open("spot/estrategias/infinity/parametros_infinity_2.0.json", "r"))         # Abrir el archivo parametros.json y cargar su contenido
exchange = parametros['exchange']                                                                   # Exchange a utilizar
activo = parametros['activo'].upper()                                                               # Activo a operar
precio_referencia = parametros['precio_referencia']                                                 # Precio de referencia
distancia_grid = parametros['distancia_grid']+0.207                                                 # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
cuenta = spot.obtener_posicion(exchange=exchange, symbol=activo)                                    # Inversión de la estrategia en cantidad del activo
tp = float(parametros['tp'])                                                                        # Take profit para detener la estrategia por completo
sl = float(parametros['sl'])                                                                        # Stop Loss para detener la estrategia por completo
tipo = parametros['direccion'].upper()                                                              # ALZA o BAJA. Si se deja en blanco opera en ambas direcciones
ganancia_grid_long = parametros['ganancia_grid_long']                                               # Ganancias por cada grid long
ganancia_grid_short = parametros['ganancia_grid_short']                                             # Ganancias por cada grid short
cantidad_moneda = cuenta*ganancia_grid_long/distancia_grid                                          # Importe en USDT para cada compra del long
cantidad_moneda_short = cuenta*ganancia_grid_short/distancia_grid                                   # Importe en USDT para cada compra del short
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
                precio_actual = spot_ws.precio_actual

            # LONG
            while grid[-1] <= precio_actual != 0:
                
                # Agregar un nuevo nivel al grid
                nuevo_nivel = round(grid[-1]*(1+distancia_grid/100),decimales_precio)
                if nuevo_nivel not in grid:
                    grid.append(nuevo_nivel)
                
                # Consultar precio actual
                if iniciar_estrategia == True:
                    precio_actual = spot_ws.precio_actual
                else:
                    precio_actual = spot.precio_actual_activo(exchange=exchange, symbol=activo)
                
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
                
                # Consultar precio actual
                if iniciar_estrategia == True:
                    precio_actual = spot_ws.precio_actual
                
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
        global apalancamiento, multiplo, cantidad_moneda, cantidad_moneda_short

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

        # Cantidad de la 1ra posicion a colocar
        if multiplo >= 1:
            cantidad_moneda = round(cantidad_moneda/multiplo)*multiplo
        
        # Imprimir Parametros
        print("")
        print("-----------------------------------------")
        print("INFINITY 2.0 - SPOT")
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
        print("Cantidad de cada venta:", round(cantidad_moneda,decimales_moneda), activo, f"({round(cantidad_moneda*precio_venta,2)} USDT)")
        print(f"Distancia entre cada grid: {distancia_grid}%")
        print(f"Ganancas del grid long: {ganancia_grid_long}%")
        print("Cuenta:", cuenta, activo)
        print("-----------------------------------------")
        print("Precio actual:", precio_actual, "USDT")
        print("Proxima compra:", precio_compra, "USDT")
        print("Próxima venta:", precio_venta, "USDT")
        print("Primera venta:", round(cantidad_moneda,decimales_moneda), activo.upper(), f"({round(cantidad_moneda*precio_venta,2)} USDT)")
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

# FUnción que se encarga de entrar la próxima compra y la próxima venta
# ---------------------------------------------------------------------
def prox_compra_venta():
    try:
        # Variables globales
        global precio_actual, grid

        # Cosultar el precio actual
        if iniciar_estrategia == True:
            precio_actual = spot_ws.precio_actual
        else:
            precio_actual = spot.precio_actual_activo(exchange=exchange, symbol=activo)
        
        # Recorrer el grid y encontrar el próximo precio de compra y venta
        prox_compra = 0
        prox_venta = 0
        while prox_compra == 0 or prox_venta == 0:
            for grilla in grid:
                if grilla <= precio_actual < grilla*(1+distancia_grid/100):
                    prox_compra = grilla
                    prox_venta = grid[grid.index(grilla)+1]
            
                # Cosultar el precio actual
                if iniciar_estrategia == True:
                    precio_actual = spot_ws.precio_actual
                else:
                    precio_actual = spot.precio_actual_activo(exchange=exchange, symbol=activo)

        #print(prox_compra, prox_venta)
        return prox_compra, prox_venta
    
    except Exception as e:
        print("ERROR EN prox_compra_venta()")
        print(e)
        print("")
# ---------------------------------------------------------------------

# Función que actualiza el estado de las parejas de compra y venta long
# ---------------------------------------------------------------------
def actualizar_parejas(exchange, symbol):
    try:

        ti = time.time()

        if tipo.upper() == "" or tipo.upper() == "LONG":

            #Obtener historial de ordenes
            historial_ordenes = spot.obtener_historial_ordenes(exchange=exchange, symbol=symbol)
            
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
                                pareja['compra']['cantidad'] = float(orden['qty'])
                                pareja['compra']['price'] = float(orden['price'])
                                pareja['compra']['monto'] = pareja['compra']['cantidad']*pareja['compra']['price']
                                pareja['general']['beneficios'] = 0.998*(pareja['venta']['monto']-pareja['compra']['monto'])
                                mostrar_lista(parejas_compra_venta)
                                #print(json.dumps(parejas_compra_venta,indent=2))
                        
                        # BINANCE
                        if exchange.upper() == "BINANCE":

                            # Obtener la orden de compra en Binance
                            if orden['status'] == "FILLED" and pareja['compra']['ejecutada'] == False:
                                pareja['compra']['ejecutada'] = True
                                pareja['compra']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['compra']['cantidad'] = float(orden['qty'])
                                pareja['compra']['price'] = float(orden['price'])
                                pareja['compra']['monto'] = pareja['compra']['cantidad']*pareja['compra']['price']
                                pareja['general']['beneficios'] = 0.998*(pareja['venta']['monto']-pareja['compra']['monto'])
                                mostrar_lista(parejas_compra_venta)
                                #print(json.dumps(parejas_compra_venta,indent=2))
                    
                    # Obtener la orden de venta
                    if orden['orderId'] == pareja['venta']['orderId']:
                        
                        # BYBIT
                        if exchange.upper() == "BYBIT":
                    
                            # Obtener la orden de venta en Bybit
                            if orden['orderStatus'] == "Filled" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = float(orden['qty'])
                                pareja['venta']['price'] = float(orden['price'])
                                pareja['venta']['monto'] = pareja['venta']['cantidad']*pareja['venta']['price']
                                mostrar_lista(parejas_compra_venta)
                                #print(json.dumps(parejas_compra_venta,indent=2))
                        
                        # BINANCE
                        if exchange.upper() == "BINANCE":
                    
                            # Obtener la orden de venta en Binance
                            if orden['status'] == "FILLED" and pareja['venta']['ejecutada'] == False:
                                pareja['venta']['ejecutada'] = True
                                pareja['venta']['fecha_ejecucion'] = datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p")
                                pareja['venta']['cantidad'] = float(orden['qty'])
                                pareja['venta']['price'] = float(orden['price'])
                                pareja['venta']['monto'] = pareja['venta']['cantidad']*pareja['venta']['price']
                                mostrar_lista(parejas_compra_venta)
                                #print(json.dumps(parejas_compra_venta,indent=2))

        #print("Parejas long actualizadas", time.time()-ti, "segundos")
    
    except Exception as e:
        print("ERROR EN LA FUNCION actualizar_pareja_long()")
        print(e)
        print("")
# ---------------------------------------------------------------------

# Función que limpia las listas de las parejas
# --------------------------------------------
def limpiar_parejas():
    try:

        # Variables globales
        global parejas_compra_venta, parejas_compra_venta_short
        
        while iniciar_estrategia:
            
            if parejas_compra_venta != []:

                ti = time.time()
                    
                actualizar_parejas(exchange=exchange, symbol=activo)
                for pareja in parejas_compra_venta:
                    
                    # LONG
                    if tipo.upper() == "LONG":

                        # Remover parejas sin no hay posición
                        posicion = spot.obtener_posicion(exchange, activo)
                        if posicion == 0:
                                
                            if pareja['compra']['ejecutada'] and not(pareja['venta']['ejecutada']):
                                print("Removiendo pareja...", pareja)
                                print("")
                                
                                if pareja in parejas_compra_venta:
                                    parejas_compra_venta.remove(pareja)
                                    mostrar_lista(parejas_compra_venta)
                                    
                        # Remover parejas si no hay ordenes abiertas
                        ordenes_abiertas = spot.obtener_ordenes(exchange, activo)
                        if not(pareja['compra']['ejecutada']):
                            orden_puesta = False
                            
                            if ordenes_abiertas != []:
                                
                                # Verificar si hay una orden limite
                                for orden in ordenes_abiertas:

                                    # BYBIT
                                    # Verificar si hay una orden limite
                                    if exchange == "BYBIT":
                                        if 0.999*pareja['compra']['price'] <= float(orden['price']) <= 1.001*pareja['compra']['price'] and orden['positionIdx'] == 1 and orden['side'] == "Buy":
                                            orden_puesta = True
                                        
                                        # Verificar si hay una orden condicional
                                        if orden['triggerPrice'] != "":
                                            if 0.999*pareja['compra']['price'] <= float(orden['triggerPrice']) <= 1.001*pareja['compra']['price'] and orden['positionIdx'] == 1 and orden['side'] == "Buy":
                                                orden_puesta = True
                                    
                                    # BINANCE
                                    # Verificar si hay una orden limite
                                    if exchange == "BINANCE":
                                        if 0.999*pareja['compra']['price'] <= float(orden['price']) <= 1.001*pareja['compra']['price'] and orden['side'] == "BUY":
                                            orden_puesta = True
                                        
                                        # Verificar si hay una orden condicional
                                        if orden['stopPrice'] != "":
                                            if 0.999*pareja['compra']['price'] <= float(orden['stopPrice']) <= 1.001*pareja['compra']['price'] and orden['side'] == "Buy":
                                                orden_puesta = True
                                
                                if not(orden_puesta):
                                    print("Removiendo pareja...", pareja)
                                    print("")
                                    
                                    if pareja in parejas_compra_venta:
                                        parejas_compra_venta.remove(pareja)
                                        mostrar_lista(parejas_compra_venta)
                    
                    # SHORT
                    if tipo.upper() == "SHORT":

                        # Remover parejas si no hay posición
                        posicion = spot.obtener_posicion(exchange, activo)
                        if posicion == 0:
                            
                            if pareja['venta']['ejecutada'] and not(pareja['compra']['ejecutada']):
                                print("Removiendo pareja...", pareja)
                                
                                if pareja in parejas_compra_venta_short:
                                    parejas_compra_venta_short.remove(pareja)
                                    mostrar_lista(parejas_compra_venta_short)

                        # Remover parejas si no hay ordenes abiertas
                        ordenes_abiertas = spot.obtener_ordenes(exchange, activo)
                        if not(pareja['venta']['ejecutada']):
                            orden_puesta = False
                            
                            if ordenes_abiertas != []:
                                
                                for orden in ordenes_abiertas:

                                    # BYBIT
                                    # Verificar si hay una orden limite
                                    if 0.999*pareja['venta']['price'] <= float(orden['price']) <= 1.001*pareja['venta']['price'] and orden['positionIdx'] == 2 and orden['side'] == "Sell":
                                        orden_puesta = True
                                    
                                    # Verificar si hay una orden condicional
                                    if orden['triggerPrice'] != "":
                                        if 0.999*pareja['venta']['price'] <= float(orden['triggerPrice']) <= 1.001*pareja['venta']['price'] and orden['positionIdx'] == 2 and orden['side'] == "Sell":
                                            orden_puesta = True
                                    
                                    # BINANCE
                                    # Verificar si hay una orden limite
                                    if 0.999*pareja['venta']['price'] <= float(orden['price']) <= 1.001*pareja['venta']['price'] and orden['side'] == "SELL":
                                        orden_puesta = True
                                    
                                    # Verificar si hay una orden condicional
                                    if orden['stopPrice'] != "":
                                        if 0.999*pareja['venta']['price'] <= float(orden['stopPrice']) <= 1.001*pareja['venta']['price'] and orden['side'] == "SELL":
                                            orden_puesta = True
                                
                                if not(orden_puesta):
                                    print("Removiendo pareja short...", pareja)
                                    
                                    if pareja in parejas_compra_venta_short:
                                        parejas_compra_venta_short.remove(pareja)
                                        mostrar_lista(parejas_compra_venta_short)
                    
                if time.time()-ti > 60:
                    print("Parejas limpias", round(time.time()-ti, 2), "segundos")
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
                precio_actual = spot_ws.precio_actual

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
                orddenes_abiertas = spot.obtener_ordenes(exchange=exchange, symbol=symbol)
                actualizar_parejas(exchange=exchange, symbol=symbol)
                for pareja in parejas_compra_venta:
                    for orden in orddenes_abiertas:
                        if not(pareja["venta"]['ejecutada']):

                            # Verificar la orden limite
                            if 0.999*pareja["compra"]['price'] < prox_compra < 1.001*pareja["compra"]['price']:
                                orden_compra_puesta = True
                            
                            # Verificar la orden condicional
                            if 0.999*pareja["compra"]['price'] < prox_venta < 1.001*pareja["compra"]['price']:
                                orden_condicional_compra_puesta = True
                                
                # Cantidad de cada compra
                qty = round(cantidad_moneda,decimales_moneda)
                
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                orden_compra = None
                
                # Colocar la orden limite de compra y crear la pareja de compra_veta
                if not(orden_compra_puesta):
                    if spot.obtener_posicion(exchange,"USDT") > qty*precio_actual and precio_actual > prox_compra:
                        orden_compra = spot.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_compra, side="BUY")
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
                            
                # Colocar la orden condicional de compra y crear la pareja de compra_veta
                if not(orden_condicional_compra_puesta) and condicional_long:
                    if spot.obtener_posicion(exchange,"USDT") > qty*precio_actual and precio_actual < prox_venta:
                        orden_compra = spot.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_venta, side="BUY")
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
                                                                    "price": round(prox_venta*(1+distancia_grid/100),decimales_precio),
                                                                    "cantidad": orden_compra['qty'],
                                                                    "monto": orden_compra['qty']*round(prox_venta*(1+distancia_grid/100),decimales_precio),
                                                                    "ejecutada": False,
                                                                    "fecha_ejecucion" : "-"
                                                                    },
                                                        "sl": {
                                                                    "orderId": ""
                                                                    }
                                                        })
                
                # Imprimir cambios
                if orden_compra != None:
                    mostrar_lista(parejas_compra_venta)
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

# Función que coloca las ordenes de venta para SHORT
# --------------------------------------------------
def ordenes_venta_short(exchange, symbol):
    try:
        nueva_compra = 0
        nueva_venta = 0
        while iniciar_estrategia:
            if tipo.upper() == "" or tipo.upper() == "SHORT":
                
                # Consultar precio actual
                precio_actual = spot_ws.precio_actual

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
                
                actualizar_parejas(exchange=exchange, symbol=symbol)
                for pareja in parejas_compra_venta:
                    if not(pareja["compra"]['ejecutada']):
                            
                        # Verificar orden limite
                        if 0.999*pareja["venta"]['price'] < prox_venta < 1.001*pareja["venta"]['price']:
                            orden_venta_puesta = True
                        
                        # Verificar orden condicional
                        if 0.999*pareja["venta"]['price'] < prox_compra < 1.001*pareja["venta"]['price']:
                            orden_condicional_venta_puesta = True
                
                # Cantidad de cada compra
                qty = round(cantidad_moneda,decimales_moneda)
                # Definir la cantidad según el múltiplo
                if multiplo >= 1:
                    qty = round(qty/multiplo)*multiplo
                
                orden_venta = None
                
                # Colocar la orden limite de venta y crear la pareja de compra_veta
                if not(orden_venta_puesta):
                    if spot.obtener_posicion(exchange,activo) > qty and precio_actual < prox_venta:
                        orden_venta = spot.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=qty, price=prox_venta, side="SELL")
                        if orden_venta != None:
                            parejas_compra_venta.insert(0,{
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
                
                # Colocar la orden condicional de compra y crear la pareja de compra_veta
                if not(orden_condicional_venta_puesta) and condicional_short:
                    if spot.obtener_posicion(exchange,activo) > qty and precio_actual > prox_compra:
                        orden_venta = spot.nueva_orden(exchange=exchange, symbol=symbol, order_type="CONDITIONAL", quantity=qty, price=prox_compra, side="SELL")
                        if orden_venta != None:
                            parejas_compra_venta.insert(0,{
                                                        "general": {
                                                                    "fecha": datetime.now().strftime("%Y-%m-%d - %I:%M:%S %p"),
                                                                    "beneficios": 0
                                                                    },
                                                        "compra": {
                                                                    "orderId": "",
                                                                    "price": round(prox_compra/(1+distancia_grid/100),decimales_precio),
                                                                    "cantidad": orden_venta['qty'],
                                                                    "monto": orden_venta['qty']*round(prox_compra/(1+distancia_grid/100),decimales_precio),
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
                
                # Imprimir cambios
                if orden_venta != None:
                    mostrar_lista(parejas_compra_venta)
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

# Funció que coloca lsa ordenes de compra para SHORT
# --------------------------------------------------
def ordenes_compra_short(exchange, symbol):
    try:
        while iniciar_estrategia:

            if tipo.upper() == "" or tipo.upper() == "SHORT":
                
                # Colocar la orden de compra y actualiza la pareja de compra_veta
                for pareja in parejas_compra_venta:
                    if pareja["venta"]['ejecutada'] and pareja["compra"]['orderId'] == "":
                        
                        # Colocar orden de compra
                        if precio_actual > pareja["compra"]['price']:
                            orden = spot.nueva_orden(exchange=exchange, symbol=symbol, order_type="LIMIT", quantity=pareja["compra"]['cantidad'], price=pareja["compra"]['price'], side="BUY")
                        else:
                            orden = spot.nueva_orden(exchange=exchange, symbol=symbol, order_type="MARKET", quantity=pareja["compra"]['cantidad'], price=pareja["compra"]['price'], side="BUY")

                        # Verificar que la respuesta sea válida antes de modificar la pareja
                        if orden != None:
                            pareja["compra"]['orderId'] = orden['orderId']
                            mostrar_lista(parejas_compra_venta)
                            print("Grid Actual:")
                            print(grid)
                            print("Cantidad de grillas:", len(grid))
                            print("")
                            #print(json.dumps(parejas_compra_venta,indent=2))
    
    except Exception as e:
        print("ERROR EN LA FUNCION ordenes_venta()")
        print(e)
        print("")
# --------------------------------------------------
'''
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
'''
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
        draw.text((180, 30), f"{round(balance_inicial,2)} {activo}", font=font, fill=text_color)
        draw.text((10, 50), f"Balance actual:", font=font, fill=text_color)
        draw.text((180, 50), f"{spot.obtener_posicion(exchange,activo)} USDT", font=font, fill=text_color)
        
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
        image.save('spot/estrategias/infinity/output.png')

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
        return 100*(spot.obtener_posicion(exchange,activo) - balance_inicial)/balance_inicial
    
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
        spot.cancelar_orden(exchange, activo, orderId="")
        print("ORDENES CERRADAS!")
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

        # Detener estrategia por Take Profit
        if ((ganancia_actual() > 1.00369*tp and 100*(ganancias_grid)/balance_inicial > 1.00369*tp) or ganancia_actual() > 1.09*tp) and tp > 0:
            iniciar_estrategia = False
            cerrar_todo()
            mostrar_lista(parejas_compra_venta)
            print("ESTRATEGIA DETENIDA POR TP!!!")
            print("")

        # Detener estrategia por Stop Loss    
        if ganancia_actual() <= (-1)*(0.9*sl) and sl > 0:
            iniciar_estrategia = False
            cerrar_todo()
            mostrar_lista(parejas_compra_venta)
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
            #margen()

            # Gestionar la  dirección
            direccion()
            time.sleep(60)
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN auxiliar()")
        print(e)
        print("")
#--------------------------------------------

# FUNCIÓN QUE DETECTA LA TENDENCIA DE UN ACTIVO
# ---------------------------------------------
def detectar_tendencia(exchange, symbol):
    
    from binance.client import Client
    from pybit.unified_trading import HTTP
    import json

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
                velas = client.get_klines(symbol=symbol, interval=interval, limit=cantidad_velas)
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
                velas = session.get_kline(category="spot", symbol=symbol, interval=interval, limit=cantidad_velas)['result']['list']

            velas.sort()
            return velas
        
        except Exception as e:
            print("ERROR EN LA FUNCIÓN. obtener_velas_precio()")
            print(e)
            print("")
            velas = []
            return velas
    #---------------------------------------------------------------------------------------

    # FUNCIÓN QUE DETERMINA LA TENDENCIA SEGÚN LAS VELAS
    # --------------------------------------------------
    def tendencia(symbol,interval):
        try:
            # Incializar variables
            velas = obtener_velas_precio(symbol,interval)
            vela_inicial_apertura = float(velas[0][1])
            vela_medio_apertura = float(velas[1][1])
            vela_medio_cierre = float(velas[1][4])
            vela_final_cierre = float(velas[2][4])
            
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
    def detector():
        try:
            alcistas = 0
            bajistas = 0
            for intervalo in intervalos:
                direccion = tendencia(symbol,intervalo)
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
    return detector()
# ---------------------------------------------

# Función que genera las direcciones
#-----------------------------------
def direccion():
    try:

        # Correr el detector de tendencia
        tendencia = detectar_tendencia(exchange,activo)
        
        # Cambiar la dirección a LONG
        if tendencia[0] == "ALCISTA":
            if tipo != "LONG":
                print("Cambio de tendencia!", tendencia[0])
                print("")
                parametros['direccion'] = "LONG"
                json.dump(parametros, open("spot/estrategias/infinity/parametros_infinity_2.0.json", "w"), indent=4)
        
        # Cambiar la dirección a SHORT
        if tendencia[0] == "BAJISTA":
            if tipo != "SHORT":
                print("Cambio de tendencia!", tendencia[0])
                print("")
                parametros['direccion'] = "SHORT"
                json.dump(parametros, open("spot/estrategias/infinity/parametros_infinity_2.0.json", "w"), indent=4)
        
        # Cambiar la dirección a RANGO
        if tendencia[0] == "RANGO":
            if tipo != "":
                print("Cambio de tendencia!", tendencia[0])
                print("")
                parametros['direccion'] = ""
                json.dump(parametros, open("spot/estrategias/infinity/parametros_infinity_2.0.json", "w"), indent=4)
        

        # Obtener ordenes abiertas
        ordenes_abiertas = spot.obtener_ordenes(exchange, activo)
        
        if tipo.upper() == "LONG":

            # Cancelar todas las ordenes short
            for orden in ordenes_abiertas:
                if exchange == "BINANCE":
                    if orden['side'] == "SELL":
                        spot.cancelar_orden(exchange,activo,orden['orderId'])
        
        if tipo.upper() == "SHORT":

            # Cancelar todas las ordenes long
            for orden in ordenes_abiertas:
                if exchange == "BINANCE":
                    if orden['side'] == "BUY":
                        spot.cancelar_orden(exchange,activo,orden['orderId'])
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN direccion()")
        print(e)
        print("")
#-----------------------------------

# Iniciar estrategia
iniciar_estrategia = False

# Balance inicial
balance_inicial = spot.obtener_posicion(exchange,activo)

# Consultar precio actual
precio_actual = spot.precio_actual_activo(exchange=exchange, symbol=activo)
            
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
if precio_actual > 30000:
    decimales_moneda = 5

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
hilo_precio_actual = threading.Thread(target=spot_ws.precio_actual_activo, args=(exchange, activo))
hilo_precio_actual.daemon = True
hilo_precio_actual.start()

# Consultar precio actual
precio_actual = spot_ws.precio_actual
while precio_actual == 0:
    precio_actual = spot_ws.precio_actual

# Iniciar Hilo de las ordenes compra
hilo_ordenes_compra = threading.Thread(target=ordenes_compra, args=(exchange,activo))
hilo_ordenes_compra.daemon = True
hilo_ordenes_compra.start()

# Iniciar Hilo de las ordenes venta_short
hilo_ordenes_venta_short = threading.Thread(target=ordenes_venta_short, args=(exchange,activo))
hilo_ordenes_venta_short.daemon = True
hilo_ordenes_venta_short.start()

# Iniciar Hilo que limpia las listas
hilo_limpiar_listas = threading.Thread(target=limpiar_parejas)
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
        parametros = json.load(open("spot/estrategias/infinity/parametros_infinity_2.0.json", "r"))         # Abrir el archivo parametros.json y cargar su contenido
        exchange = parametros['exchange']                                                                   # Exchange a utilizar
        activo = parametros['activo'].upper()                                                               # Activo a operar
        precio_referencia = parametros['precio_referencia']                                                 # Precio de referencia
        distancia_grid = parametros['distancia_grid']+0.207                                                 # Distancia en porcentaje entre cada grilla (ganancia + comisiones)
        cuenta = spot.obtener_posicion(exchange=exchange, symbol=activo)                                    # Inversión de la estrategia en cantidad del activo
        tp = float(parametros['tp'])                                                                        # Take profit para detener la estrategia por completo
        sl = float(parametros['sl'])                                                                        # Stop Loss para detener la estrategia por completo
        tipo = parametros['direccion'].upper()                                                              # ALZA o BAJA. Si se deja en blanco opera en ambas direcciones
        ganancia_grid_long = parametros['ganancia_grid_long']                                               # Ganancias por cada grid long
        ganancia_grid_short = parametros['ganancia_grid_short']                                             # Ganancias por cada grid short
        cantidad_moneda = cuenta*ganancia_grid_long/distancia_grid                                          # Importe en USDT para cada compra del long
        cantidad_moneda_short = cuenta*ganancia_grid_short/distancia_grid                                   # Importe en USDT para cada compra del short
        condicional_long = parametros['condicional_long']
        condicional_short = parametros['condicional_short']
        # ---------------------------

        # Verificar que el hilo detener_estrategia este activo
        if not(hilo_detener_estrategia.is_alive()):
            hilo_detener_estrategia = threading.Thread(target=detener_estrategia)
            hilo_detener_estrategia.daemon = True
            hilo_detener_estrategia.start()

        # Verificar que el hilo del precio actual este activo
        if not(hilo_precio_actual.is_alive) or spot_ws.precio_actual == 0:
            hilo_precio_actual = threading.Thread(target=spot_ws.precio_actual_activo, args=(exchange, activo))
            hilo_precio_actual.daemon = True
            hilo_precio_actual.start()

        # Verificar que el hilo actualizar grid este activo
        if not(hilo_actualizar_grid.is_alive()):
            hilo_actualizar_grid = threading.Thread(target=actualizar_grid)
            hilo_actualizar_grid.daemon = True
            hilo_actualizar_grid.start()

        # Verificar que el hilo limpiar listas este activo
        if not(hilo_limpiar_listas.is_alive()):
            hilo_limpiar_listas = threading.Thread(target=limpiar_parejas)
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
        
        # SHORT
        if tipo.upper() == "" or tipo.upper() == "SHORT":
            
            # Verificar que el hilo de compras este activo
            if not(hilo_ordenes_venta_short.is_alive()):
                hilo_ordenes_venta_short = threading.Thread(target=ordenes_venta_short, args=(exchange,activo))
                hilo_ordenes_venta_short.daemon = True
                hilo_ordenes_venta_short.start()
    
    except Exception as e:
        print("ERROR EN EL PROGRAMA PRINCIPAL")
        print("")

cerrar_todo()
cerrar_todo()
mostrar_lista(parejas_compra_venta)
cerrar_todo()
cerrar_todo()