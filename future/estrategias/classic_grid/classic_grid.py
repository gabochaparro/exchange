'''
Peograma que opera en diferententes exchange utilizando el grid de futuro clásico 
'''

# Importar paquetes y librerias
# -----------------------------
import json
import time
import shutil
import future
import inverse
import inverse_ws
import future_ws
import threading
# -----------------------------

# Abrir el archivo parametros_iniciales.json y cargar su contenido
# ----------------------------------------------------------------
parametros = json.load(open("future/estrategias/classic_grid/parametros_iniciales.json", "r"))
# ----------------------------------------------------------------

# Crear una copia temporal del archivo json con los parametros
# ------------------------------------------------------------
fecha_inicio = int(time.time())*1000
if parametros['inverso']:
    parametros_copia = f"future/estrategias/classic_grid/parametros/{parametros['activo'].upper()}_{parametros['exchange'].upper()}_INVERSO_{fecha_inicio}.json"
else:
    parametros_copia = f"future/estrategias/classic_grid/parametros/{parametros['activo'].upper()}_{parametros['exchange'].upper()}_LINEAL_{fecha_inicio}.json"
shutil.copy("future/estrategias/classic_grid/parametros_iniciales.json", parametros_copia)
# ------------------------------------------------------------

# PARAMETROS INCIALES
# -------------------
exchange = parametros['exchange'].upper()
tipo = parametros['direccion'].upper()
symbol = parametros['activo'].upper()
inverso = parametros['inverso']
apalancamiento = parametros['apalancamiento']
precio_minimo = parametros['precio_minimo']
precio_maximo = parametros['precio_maximo']
numero_regillas = parametros['numero_regillas']
inversion = parametros['inversion']                                 # En inverso colocar la cantidad del activo
precio_activación = parametros['precio_activación']
activacion_instantanea = parametros['activacion_instantanea']
ganacia_esperada = parametros['ganacia_esperada']
max_perdida = parametros['max_perdida']
porcentage_ganancia = parametros['porcentage_ganancia']
porcentage_perdida = parametros['porcentage_perdida']
precio_tp = parametros['precio_tp']
precio_sl = parametros['precio_sl']
pausa = parametros['pausa']
# -------------------

# Variables iniciales
# -------------------
if inverso:
    balance_inicial = inverse.patrimonio(exchange, symbol)
    precio_actual = inverse.precio_actual_activo(exchange, symbol)
else:
    balance_inicial = future.patrimonio(exchange)
    precio_actual = future.precio_actual_activo(exchange, symbol)
# -------------------

# Generar el grid
# ---------------
grilla = []
paso = (precio_maximo - precio_minimo) / (numero_regillas - 1)
i = 0
while i < numero_regillas:
    if inverso:
        grilla.append(inverse.normalizar_precio(exchange, symbol, precio_minimo + i * paso))
    else:
        grilla.append(future.normalizar_precio(exchange, symbol, precio_minimo + i * paso))
    i = i + 1
# ---------------

# Cantidad por cada orden
# -----------------------
if inverso:
    cantidad_por_nivel = inversion*apalancamiento*precio_actual/(numero_regillas-1)
else:
    cantidad_por_nivel = (inversion*apalancamiento/precio_actual)/(numero_regillas-1)
# -----------------------

# Colocar la primera orden
# ------------------------
if activacion_instantanea and tipo == "LONG":
    print("")
    print(f"Colocando {len(grilla)-1} ordenes...")
    print("")
    for precio in grilla:
        if precio_actual < precio != grilla[0]:
            print(f"Colocando orden No: {grilla.index(precio)}")
            if inverso:
                inverse.nueva_orden(exchange=exchange,
                                    symbol=symbol,
                                    order_type="MARKET",
                                    quantity=cantidad_por_nivel,
                                    price=precio_actual,
                                    side="BUY",
                                    leverage=apalancamiento,
                                    tp=precio)
            else:
                future.nueva_orden(exchange=exchange,
                                    symbol=symbol,
                                    order_type="MARKET",
                                    quantity=cantidad_por_nivel,
                                    price=precio_actual,
                                    side="BUY",
                                    leverage=apalancamiento,
                                    tp=precio)
        
        elif abs(precio-precio_actual) > abs(grilla[0]-grilla[1]) and (grilla[grilla.index(precio)-1] < precio_actual < precio):
            print(f"Colocando orden No: {grilla.index(precio)}")
            if inverso:
                inverse.nueva_orden(exchange=exchange,
                                    symbol=symbol,
                                    order_type="LIMIT",
                                    quantity=cantidad_por_nivel,
                                    price=precio,
                                    side="BUY",
                                    leverage=apalancamiento,
                                    tp=grilla[grilla.index(precio)+1])
            else:
                future.nueva_orden(exchange=exchange,
                                    symbol=symbol,
                                    order_type="LIMIT",
                                    quantity=cantidad_por_nivel,
                                    price=precio,
                                    side="BUY",
                                    leverage=apalancamiento,
                                    tp=grilla[grilla.index(precio)+1])

elif tipo == "LONG":
    print("")
    print(f"Colocando {len(grilla)-1} ordenes...")
    print("")
    for precio in grilla:
        if precio_activación < precio_actual:
            if precio_activación < precio != grilla[0]:
                print(f"Colocando orden No: {grilla.index(precio)}")
                if inverso:
                    inverse.nueva_orden(exchange=exchange,
                                        symbol=symbol,
                                        order_type="LIMIT",
                                        quantity=cantidad_por_nivel,
                                        price=precio_activación,
                                        side="BUY",
                                        leverage=apalancamiento,
                                        tp=precio)
                else:
                    future.nueva_orden(exchange=exchange,
                                        symbol=symbol,
                                        order_type="LIMIT",
                                        quantity=cantidad_por_nivel,
                                        price=precio_activación,
                                        side="BUY",
                                        leverage=apalancamiento,
                                        tp=precio)
            
            elif precio_activación > precio and abs(precio-precio_activación) > abs(grilla[0]-grilla[1]) and (grilla[grilla.index(precio)-1] < precio_actual < precio):
                print(f"Colocando orden No: {grilla.index(precio)}")
                if inverso:
                    inverse.nueva_orden(exchange=exchange,
                                        symbol=symbol,
                                        order_type="LIMIT",
                                        quantity=cantidad_por_nivel,
                                        price=precio,
                                        side="BUY",
                                        leverage=apalancamiento,
                                        tp=grilla[grilla.index(precio)+1])
                else:
                    future.nueva_orden(exchange=exchange,
                                        symbol=symbol,
                                        order_type="LIMIT",
                                        quantity=cantidad_por_nivel,
                                        price=precio,
                                        side="BUY",
                                        leverage=apalancamiento,
                                        tp=grilla[grilla.index(precio)+1])

if activacion_instantanea and tipo == "SHORT":
    print("")
    print(f"Colocando {len(grilla)-1} ordenes...")
    print("")
    for precio in grilla:
        if precio_actual > precio != grilla[-1]:
            print(f"Colocando orden No: {grilla.index(precio)}")
            if inverso:
                inverse.nueva_orden(exchange=exchange,
                                    symbol=symbol,
                                    order_type="MARKET",
                                    quantity=cantidad_por_nivel,
                                    price=precio_actual,
                                    side="SELL",
                                    leverage=apalancamiento,
                                    tp=precio)
            else:
                future.nueva_orden(exchange=exchange,
                                    symbol=symbol,
                                    order_type="MARKET",
                                    quantity=cantidad_por_nivel,
                                    price=precio_actual,
                                    side="SELL",
                                    leverage=apalancamiento,
                                    tp=precio)
        
        elif abs(precio_actual-precio) > abs(grilla[0]-grilla[1]) and (precio < precio_actual < grilla[grilla.index(precio)+1]):
            print(f"Colocando orden No: {grilla.index(precio)}")
            if inverso:
                inverse.nueva_orden(exchange=exchange,
                                    symbol=symbol,
                                    order_type="LIMIT",
                                    quantity=cantidad_por_nivel,
                                    price=precio,
                                    side="SELL",
                                    leverage=apalancamiento,
                                    tp=grilla[grilla.index(precio)-1])
            else:
                future.nueva_orden(exchange=exchange,
                                    symbol=symbol,
                                    order_type="LIMIT",
                                    quantity=cantidad_por_nivel,
                                    price=precio,
                                    side="SELL",
                                    leverage=apalancamiento,
                                    tp=grilla[grilla.index(precio)-1])

elif tipo == "SHORT":
    print("")
    print(f"Colocando {len(grilla)-1} ordenes...")
    print("")
    for precio in grilla:
        if precio_activación > precio_actual:
            if precio_activación > precio != grilla[-1]:
                print(f"Colocando orden No: {grilla.index(precio)}")
                if inverso:
                    inverse.nueva_orden(exchange=exchange,
                                        symbol=symbol,
                                        order_type="LIMIT",
                                        quantity=cantidad_por_nivel,
                                        price=precio_activación,
                                        side="SELL",
                                        leverage=apalancamiento,
                                        tp=precio)
                else:
                    future.nueva_orden(exchange=exchange,
                                        symbol=symbol,
                                        order_type="LIMIT",
                                        quantity=cantidad_por_nivel,
                                        price=precio_activación,
                                        side="SELL",
                                        leverage=apalancamiento,
                                        tp=precio)
            
            elif precio_activación < precio and abs(precio_activación-precio) > abs(grilla[0]-grilla[1]) and (precio < precio_actual < grilla[grilla.index(precio)+1]):
                print(f"Colocando orden No: {grilla.index(precio)}")
                if inverso:
                    inverse.nueva_orden(exchange=exchange,
                                        symbol=symbol,
                                        order_type="LIMIT",
                                        quantity=cantidad_por_nivel,
                                        price=precio,
                                        side="SELL",
                                        leverage=apalancamiento,
                                        tp=grilla[grilla.index(precio)-1])
                else:
                    future.nueva_orden(exchange=exchange,
                                        symbol=symbol,
                                        order_type="LIMIT",
                                        quantity=cantidad_por_nivel,
                                        price=precio,
                                        side="SELL",
                                        leverage=apalancamiento,
                                        tp=grilla[grilla.index(precio)-1])
# ------------------------

# FUNCION QUE CIERRA TODO
# -----------------------
def cerrar_todo():
    try:

        print("CERRANDO ESTRTATEGIA...")
        
        # Cancelar todas las ordenes
        if inverso:
            inverse.cancelar_orden(exchange, symbol, orderId="")
        else:
            future.cancelar_orden(exchange, symbol, orderId="")
        
        # Cerrar posiciones
        if inverso:
            posiciones = inverse.obtener_posicion(exchange, symbol)
        else:
            posiciones = future.obtener_posicion(exchange, symbol)
        for posicion in posiciones:
            
            if exchange == "BYBIT":
                # Long
                if posicion['positionIdx'] == 0 and posicion['side'] == "Buy":
                    if posicion['size'] != "0":
                        if inverso:
                            inverse.cerrar_posicion(exchange, symbol, "LONG")
                        else:
                            future.cerrar_posicion(exchange, symbol, "LONG")
                
                if posicion['positionIdx'] == 1:
                    if posicion['size'] != "0":
                        if inverso:
                            inverse.cerrar_posicion(exchange, symbol, "LONG")
                        else:
                            future.cerrar_posicion(exchange, symbol, "LONG")
                # Short
                if posicion['positionIdx'] == 0 and posicion['side'] == "Sell":
                    if posicion['size'] != "0":
                        if inverso:
                            inverse.cerrar_posicion(exchange, symbol, "SHORT")
                        else:
                            future.cerrar_posicion(exchange, symbol, "SHORT")
                
                if posicion['positionIdx'] == 2:
                    if posicion['size'] != "0":
                        if inverso:
                            inverse.cerrar_posicion(exchange, symbol, "SHORT")
                        else:
                            future.cerrar_posicion(exchange, symbol, "SHORT")
            
            if exchange == "BINANCE":
                if posiciones != []:
                    # Long
                    if posicion['positionSide'] == "LONG":
                        if posicion['notional'] != "0":
                            if inverso:
                                inverse.cerrar_posicion(exchange, symbol, "LONG")
                            else:
                                future.cerrar_posicion(exchange, symbol, "LONG")
                    # Short
                    if posicion['positionSide'] == "SHORT":
                        if posicion['notional'] != "0":
                            if inverso:
                                inverse.cerrar_posicion(exchange, symbol, "SHORT")
                            else:
                                future.cerrar_posicion(exchange, symbol, "SHORT")
        
        print("ORDENES Y POSICIONES CERRADAS!")
        print("")
        parametros['pausa'] = True
        json.dump(parametros, open(parametros_copia, "w"), indent=4)

    except Exception as e:
        print("ERROR CERRANDO TODO")
        print(e)
        print("")
# -----------------------
    
# FUNCIÓN QUE DETIENE LA ESTRATEGIA
# ---------------------------------
def detener_estrategia():
    try:
        global precio_actual
        while True:
            if inverso:
                patrimonio = inverse.patrimonio(exchange, symbol)
                if (patrimonio - balance_inicial <= max_perdida) and float(max_perdida) != 0.0:
                    cerrar_todo()
                    print("ESTRATEGIA DETENIDA POR SL DE CAPITAL")
                if (patrimonio - balance_inicial > ganacia_esperada) and float(ganacia_esperada) != 0.0:
                    cerrar_todo()
                    print("ESTRATEGIA DETENIDA POR TP DE CAPITAL")
                if ((patrimonio - balance_inicial)/balance_inicial <= porcentage_perdida/100) and float(porcentage_perdida) != 0.0:
                    cerrar_todo()
                    print("ESTRATEGIA DETENIDA POR SL PORCENTUAL")
                if ((patrimonio - balance_inicial)/balance_inicial >= porcentage_ganancia/100) and float(porcentage_ganancia) != 0.0:
                    cerrar_todo()
                    print("ESTRATEGIA DETENIDA POR TP  PORCENTUAL")
            
            else:
                if precio_actual == "":
                    precio_actual = future.precio_actual_activo(exchange,symbol)
                patrimonio = future.patrimonio(exchange)
                if (patrimonio - balance_inicial <= max_perdida) and float(max_perdida) != 0.0:
                    cerrar_todo()
                    print("ESTRATEGIA DETENIDA POR SL DE CAPITAL")
                if (patrimonio - balance_inicial > ganacia_esperada) and float(ganacia_esperada) != 0.0:
                    cerrar_todo()
                    print("ESTRATEGIA DETENIDA POR TP DE CAPITAL")
                if ((patrimonio - balance_inicial)/balance_inicial <= porcentage_perdida/100) and float(porcentage_perdida) != 0.0:
                    cerrar_todo()
                    print("ESTRATEGIA DETENIDA POR SL PORCENTUAL")
                if ((patrimonio - balance_inicial)/balance_inicial >= porcentage_ganancia/100) and float(porcentage_ganancia) != 0.0:
                    cerrar_todo()
                    print("ESTRATEGIA DETENIDA POR TP  PORCENTUAL")

            if precio_actual <= precio_sl and float(precio_sl) != 0.0:
                cerrar_todo()
                print("ESTRATEGIA DETENIDA POR SL DE PRECIO")
            if precio_actual > precio_tp and float(precio_tp) != 0.0:
                cerrar_todo()
                print("ESTRATEGIA DETENIDA POR TP DE PRECIO")

            time.sleep(1)

    except Exception as e:
        print("ERROR EN LA FUNCIÓN detener_estrategia()")
        print(e)
        print("")
# ---------------------------------

# FUNCION QUE DETECTA LOS TP
# --------------------------
def exsite_tp_en_precio(precio):
    try:
            
        if inverso:
            ordenes_abiertas = inverse.obtener_ordenes(exchange=exchange, symbol=symbol)
        else:
            ordenes_abiertas = future.obtener_ordenes(exchange=exchange, symbol=symbol)
        
        if exchange == "BYBIT":
            for orden in ordenes_abiertas:
                if orden['takeProfit'] == str(precio):
                    return True
                if (orden['triggerPrice'] == str(precio) and orden['reduceOnly']):
                    return True
        return False
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN exite_tp_en_precio()")
        print(e)
        print("")
        return False
# --------------------------

# FUNCIÓN QUE COLOCA NUEVAS ORDENES
# ---------------------------------
def colocar_nuevas_ordenes():
    try:
        # Colocar nuevas ordenese
        # -----------------------
        while not(pausa):
            for precio in grilla:

                if not(exsite_tp_en_precio(precio)) and tipo == "LONG" and precio != grilla[0] and (grilla[grilla.index(precio)-1] < precio_actual < precio):
                    if inverso:
                        inverse.nueva_orden(exchange=exchange,
                                            symbol=symbol,
                                            order_type="LIMIT",
                                            quantity=cantidad_por_nivel,
                                            price=grilla[grilla.index(precio)-1],
                                            side="BUY",
                                            leverage=apalancamiento,
                                            tp=precio)
                    else:
                        future.nueva_orden(exchange=exchange,
                                            symbol=symbol,
                                            order_type="LIMIT",
                                            quantity=cantidad_por_nivel,
                                            price=grilla[grilla.index(precio)-1],
                                            side="BUY",
                                            leverage=apalancamiento,
                                            tp=precio)
                
                if not(exsite_tp_en_precio(precio)) and tipo == "SHORT" and precio != grilla[-1] and (precio < precio_actual < grilla[grilla.index(precio)+1]):
                    if inverso:
                        inverse.nueva_orden(exchange=exchange,
                                            symbol=symbol,
                                            order_type="LIMIT",
                                            quantity=cantidad_por_nivel,
                                            price=grilla[grilla.index(precio)+1],
                                            side="SELL",
                                            leverage=apalancamiento,
                                            tp=precio)
                    else:
                        future.nueva_orden(exchange=exchange,
                                            symbol=symbol,
                                            order_type="LIMIT",
                                            quantity=cantidad_por_nivel,
                                            price=grilla[grilla.index(precio)+1],
                                            side="SELL",
                                            leverage=apalancamiento,
                                            tp=precio)

    except Exception as e:
        print("ERRP)R EN LA FUNCIÓN colocar_nuevas_ordenes()")   
        print(e)
        print("") 
# ---------------------------------

# Iniciar hilo del precio actual
# ------------------------------
if inverso:
    hilo_precio_actual = threading.Thread(target=inverse_ws.precio_actual_activo, args=(exchange, symbol))
    hilo_precio_actual.daemon = True
    hilo_precio_actual.start()
else:
    hilo_precio_actual = threading.Thread(target=future_ws.precio_actual_activo, args=(exchange, symbol))
    hilo_precio_actual.daemon = True
    hilo_precio_actual.start()
# ------------------------------

# Consultar precio actual
# -----------------------
if inverso:
    precio_actual = inverse_ws.precio_actual
else:
    precio_actual = future_ws.precio_actual
while precio_actual == None or not(hilo_precio_actual.is_alive()):
    print("ESPERANDO!!!", "PRECIO ACTUAL:", precio_actual)
    if inverso:
        precio_actual = inverse_ws.precio_actual
    else:
        precio_actual = future_ws.precio_actual
# -----------------------

# Iniciar hilo_detener_estrategia
# ------------------------------
hilo_detener_estrategia = threading.Thread(target=detener_estrategia)
hilo_detener_estrategia.daemon = True
hilo_detener_estrategia.start()
# ------------------------------

# Iniciar hilo colocar_nuevas_ordenes
# ------------------------------
hilo_colocar_nuevas_ordenes = threading.Thread(target=colocar_nuevas_ordenes)
hilo_colocar_nuevas_ordenes.daemon = True
hilo_colocar_nuevas_ordenes.start()
# ------------------------------

# Ciclo principal
# ---------------
while True:
    try:
        # Paremetros actuales
        # -------------------
        parametros = json.load(open(parametros_copia, "r"))
        apalancamiento = parametros['apalancamiento']
        precio_minimo = parametros['precio_minimo']
        precio_maximo = parametros['precio_maximo']
        numero_regillas = parametros['numero_regillas']
        inversion = parametros['inversion']                                 # En inverso colocar la cantidad del activo
        precio_activación = parametros['precio_activación']
        activacion_instantanea = parametros['activacion_instantanea']
        ganacia_esperada = parametros['ganacia_esperada']
        max_perdida = parametros['max_perdida']
        porcentage_ganancia = parametros['porcentage_ganancia']
        porcentage_perdida = parametros['porcentage_perdida']
        precio_tp = parametros['precio_tp']
        precio_sl = parametros['precio_sl']
        pausa = parametros['pausa']
        # -------------------

        # Verificar que el hilo hilo_detener_estrategia este activo
        # -------------------------------------------------------------
        if not(hilo_detener_estrategia.is_alive()):
            hilo_detener_estrategia = threading.Thread(target=detener_estrategia)
            hilo_detener_estrategia.daemon = True
            hilo_detener_estrategia.start()
        # -------------------------------------------------------------

        # Verificar que el hilo del precio actual este activo
        # ---------------------------------------------------
        if inverso:
            if not(hilo_precio_actual.is_alive()):
                hilo_precio_actual = threading.Thread(target=inverse_ws.precio_actual_activo, args=(exchange, symbol))
                hilo_precio_actual.daemon = True
                hilo_precio_actual.start()
        else:
            if not(hilo_precio_actual.is_alive()):
                hilo_precio_actual = threading.Thread(target=future_ws.precio_actual_activo, args=(exchange, symbol))
                hilo_precio_actual.daemon = True
                hilo_precio_actual.start()
        # ---------------------------------------------------
        
        # Consultar precio actual
        # -----------------------
        if inverso:
            precio_actual = inverse_ws.precio_actual
        else:
            precio_actual = future_ws.precio_actual
        # -----------------------

        # Verificar que el hilo hilo_colocar_nuevas_ordenes este activo
        # -------------------------------------------------------------
        if not(hilo_colocar_nuevas_ordenes.is_alive()):
            hilo_colocar_nuevas_ordenes = threading.Thread(target=colocar_nuevas_ordenes)
            hilo_colocar_nuevas_ordenes.daemon = True
            hilo_colocar_nuevas_ordenes.start()
        # -------------------------------------------------------------

        # Cancelar todas las ordenes
        # --------------------------
        if pausa:
            if inverso:
                ordenes = inverse.obtener_ordenes(exchange, symbol)
                for orden in ordenes:
                    if not(orden['reduceOnly']):
                        inverse.cancelar_orden(exchange, symbol, orderId=orden['orderId'])
            else:
                ordenes = future.obtener_ordenes(exchange, symbol)
                for orden in ordenes:
                    if not(orden['reduceOnly']):
                        future.cancelar_orden(exchange, symbol, orderId=orden['orderId'])
            time.sleep(1)
        # --------------------------
    
    except Exception as e:
        print("ERROR EN EL PROGRAMA PRINCIPAL")
        print(e)
        print("")
# ---------------
