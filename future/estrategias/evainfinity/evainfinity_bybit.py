# Importar librerias
#  -----------------------------------------------
try:
    import asyncio, json, logging, sys, traceback, numpy as np, time, talib
    from pybit.unified_trading import WebSocket, HTTP
except Exception as e:
    print(f"\nERROR EXPORTANDO LIBRERIAS: {e}")
    sys.exit()
#  -----------------------------------------------

# Capturar errores no manejados y configurar logger
#  -----------------------------------------------
try:
    # Configurar logging
    def configurar_logging(archivo: str = "salida/app.log", debug: bool = False):
        try:
            # 1️⃣ Crea un logger
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG if debug else logging.INFO)
            logger.handlers.clear()


            # 2️⃣ Handler para escribir en archivo
            file_handler = logging.FileHandler(archivo, mode="w", encoding="utf-8")
            file_handler.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s (%(asctime)s)", datefmt="%Y-%m-%d %H:%M:%S"))
            logger.addHandler(file_handler)

            # 3️⃣ Handler para imprimir en consola
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("\n[%(levelname)s]: %(message)s (%(asctime)s)", datefmt="%Y-%m-%d %H:%M:%S"))
            logger.addHandler(console_handler)

            logger.info("Logging configurado correctamente")

            return logger
        except:
            print(f"\nERROR CONFIGURANDO LOGGING: {traceback.format_exc()}")

    logger = configurar_logging()

    # Capturar errores no controlados (tracebacks)
    def registrar_excepciones(exc_type, exc_value, exc_traceback):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(tb)
        
    # Ejecutar registrar_excepciones() cada vez que ocurre un error no manejado 
    sys.excepthook = registrar_excepciones
except:
    print(f"\nERROR EN LA CAPTURA DE ERRORES NO MANEJADOS:\n{traceback.format_exc()}")
    sys.exit()
#  -----------------------------------------------

# precio_actual_ws()
#  -----------------------------------------------
async def precio_actual_ws(channel_type, symbol):
    global precio_actual, pausa_long, pausa_short, cierres, ema9, ema54
    
    def callback(msg):
        try:
            global precio_actual, cierres, ema9, ema54
            precio_actual = float(msg['data'][0]['close'])
            if msg['data'][0]['confirm']:
                velas = bybit_session.get_kline(category="linear", symbol=symbol, interval="5", limit=369)["result"]["list"]
                cierres = [float(x[4]) for x in reversed(velas)] # Bybit envía las velas en orden inverso, así que las revertimos
                logger.info("Historial de velas actualizado")
            cierres[-1] = precio_actual
            cierresnp = np.array(cierres, dtype=float)
            ema54 = talib.EMA(cierresnp, timeperiod=54)[-1]
            ema9 = talib.EMA(cierresnp, timeperiod=9)[-1]
        except Exception as e:
            logger.error(f"Error en el callback de kline_stream. {e}")
    
    while True:
        ws = WebSocket(testnet=False, channel_type=channel_type)
        velas = bybit_session.get_kline(category="linear", symbol=symbol, interval="5", limit=369)["result"]["list"]
        cierres = [float(x[4]) for x in reversed(velas)] # Bybit envía las velas en orden inverso, así que las revertimos
        pausa_long = True
        pausa_short = True
        logger.info("Estableciendo conexión pública...")
        ws.kline_stream(interval="5", symbol=symbol, callback=callback)
        ws.ping_interval = 20
        ws.ping_timeout = 3
        while ws.is_connected():
            await asyncio.sleep(0.000999)
        ws.exit()
#  -----------------------------------------------

# oredenes_ws()
#  -----------------------------------------------
async def oredenes_ws():
    global ordenes_abiertas, posicion, pausa_long, pausa_short
    
    def callback(msg):
        try:
            global posicion, ordenes_abiertas
            posicion = obtener_posicion(category, symbol)
            ordenes_abiertas = obtener_ordenes(category, symbol)
        except Exception as e:
            logger.error(f"Error en el callback de position_stream. {e}")
    
    while True:
        ws = WebSocket(testnet=False, channel_type="private", api_key=api_key, api_secret=api_secret)
        pausa_short = True
        pausa_long = True
        logger.info("Estableciendo conexión ws con position_stream...")
        ws.position_stream(callback=callback)
        ws.ping_interval = 20
        ws.ping_timeout = 3
        while ws.is_connected():
            await asyncio.sleep(0.000999)
        ws.exit()
#  -----------------------------------------------

# FUNCIÓN QUE OBTIENE EL MONTO DISPONIBLE DE LA CUENTA
# ----------------------------------------------------
async def patrimonio(category, symbol):
    global patrimonio_actual, balance_inicial
    patrimonio = None
    patrimonio_actual =None
    while True:
        try:
            if category == "inverse":
                symbol = symbol.upper().split("USD")[0].upper()
                patrimonio = float(bybit_session.get_wallet_balance(accountType="UNIFIED", coin=symbol)['result']['list'][0]['coin'][0]['equity'])
            if category == "linear":
                patrimonio = float(bybit_session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalEquity'])
            
            if patrimonio != None:
                balance_inicial = patrimonio if patrimonio_actual == None else balance_inicial
                patrimonio_actual = patrimonio
            else:
                logger.error("Error en patrimonio()")
            await asyncio.sleep(0.999)
        except Exception as e:
            logger.error(f"Error en patrimonio() {traceback.format_exc()}")
            await asyncio.sleep(9.99)
# ----------------------------------------------------

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(category, symbol):
    try:

        # Obtener el apalancamiento máximo
        max_leverage = bybit_session.get_instruments_info(category=category, symbol=symbol.upper())['result']['list'][0]['leverageFilter']['maxLeverage']
        return int(float(max_leverage))
    
    except Exception as e:
        logger.error(f"Error en apalancameinto_max() {traceback.format_exc()}")
# ------------------------------------------------------

# FUNCIÓN QUE CAMBIA EL APALANCAMIENTO DE UN TICK
# ------------------------------------------------------
def apalancameinto(category, symbol, leverage):
    try:
        
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(category, symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancamiento_actual = float(bybit_session.get_positions(category=category, symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if round(apalancamiento_actual,2) != round(float(leverage),2):
            bybit_session.set_leverage(category=category, symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))
    
    except Exception as e:
        logger.error(f"Error en apalancameinto() {e}")
# ------------------------------------------------------

# FUNCIÓN DE BYBIT NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------------
def nueva_orden(category, symbol, order_type, quantity, price, side, leverage, tp=0.0, sl=0.0):
    try:
        
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(category, symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancamiento_actual = float(bybit_session.get_positions(category=category, symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if round(apalancamiento_actual,2) != round(float(leverage),2):
            bybit_session.set_leverage(category=category, symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))

        # Definir el lado para el modo hedge
        if symbol.split(symbol.split("USD")[0])[-1] == "USD":
            positionSide = 0
            if side =="BUY":
                triggerDirection = 1
            if side == "SELL":
                triggerDirection = 2
        else:
            if side == "BUY":
                positionSide = 1
                triggerDirection = 1
            if side == "SELL":
                positionSide = 2
                triggerDirection = 2

        # Definir la cantidad exacta que permite bybit
        cantidad_paso = float(bybit_session.get_instruments_info(category=category, symbol=symbol)['result']['list'][0]['lotSizeFilter']['qtyStep'])
        quantity = round(quantity/cantidad_paso)*cantidad_paso

        # Definir el Tp
        tpOrderType = "Market"
        if tp > 0:
            tpOrderType = "Limit"

        # Coloca la orden "LIMIT"
        if order_type.upper() == "LIMIT":
            order = bybit_session.place_order(
                category=category,
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                price=price,
                timeinforce="GTC",
                positionIdx=positionSide,
                tpslMode = "Partial",
                tpOrderType = tpOrderType,
                takeProfit = str(tp),
                tpLimitPrice = str(tp),
                stopLoss = str(sl)
            )
        
        # Coloca la orden "MARKET"
        if order_type.upper() == "MARKET":
            order = bybit_session.place_order(
                category=category,
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                positionIdx=positionSide,
                tpslMode = "Partial",
                tpOrderType = tpOrderType,
                takeProfit = str(tp),
                tpLimitPrice = str(tp),
                stopLoss = str(sl)
            )

        # Coloca la orden "CONDITIONAL"
        if order_type.upper() == "CONDITIONAL":
            order = bybit_session.place_order(
                category=category,
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType="MARKET",
                qty=quantity,
                price=price,
                triggerPrice=price,
                triggerBy="LastPrice",
                timeinforce="GTC",
                positionIdx=positionSide,
                triggerDirection=triggerDirection,
                tpslMode = "Partial",
                tpOrderType = tpOrderType,
                takeProfit = str(tp),
                tpLimitPrice = str(tp),
                stopLoss = str(sl)
            )

        order = obtener_ordenes(category, symbol, order["result"]["orderId"])
        #print(json.dumps(order,indent=2))
        
        if order_type.upper() == "CONDITIONAL":
            price = float(order[0]["triggerPrice"])
        else:
            price = float(order[0]["price"])
        
        logger.info(f"Orden {order_type.upper()}-{side} de {order[0]['qty']} {symbol.split('USDT')[0]}  colocada en {price}. ID: {order[0]['orderId']}")

        
        return {
                "orderId": order[0]["orderId"],
                "price": price,
                "qty": float(order[0]["qty"])
                }
    
    except Exception as e:
        logger.error(f"Error en nueva_orden() {e}")
# ---------------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(category, symbol, orderId=""):
    try:
        return bybit_session.get_open_orders(category=category,symbol=symbol.upper(),orderId=orderId)["result"]['list']

    except Exception as e:
        logger.error(f"Error en obtener_ordenes() {traceback.format_exc()}")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(category, symbol, orderId):
    try:

        if orderId == "":
            print("Eliminando todas las ordenes...")
            bybit_session.cancel_all_orders(category=category,symbol=symbol)
            print("Todas las ordenes eliminadas.")
            print("")
        else:
            print(f"Eliminando orden {orderId}...")
            bybit_session.cancel_order(category=category,symbol=symbol,orderId=orderId)
            print(f"Eliminada la orden {orderId} de {symbol}.")
            print("")
    
    except Exception as e:
        logger.error(f"Error en cancelar_orden() {e}")
# -----------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(category, symbol):
    try:

        return bybit_session.get_positions(category=category, symbol=symbol.upper())["result"]["list"]

    except:
        logger.error(f"Error en obtener_posicion() {traceback.format_exc()}")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(category, symbol, positionSide, size=""):
    try:
        
        # Definir el lado segun la posición
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "Sell"
            positionIdx = 1
        if positionSide == "SHORT":
            side = "Buy"
            positionIdx = 2
        if symbol.split(symbol.split("USD")[0])[-1] == "USD":
            positionIdx = 0

        # Definir la cantidad
        if size =="":
            size = 0
            
        # Cerrar posición
        logger.info("Cerrando posición...")
        logger.info(json.dumps(bybit_session.place_order(
                                    category=category,
                                    symbol= symbol,
                                    side=side,
                                    orderType="Market",
                                    qty=str(size),
                                    reduceOnly=True,
                                    closeOnTrigger=True,
                                    positionIdx=positionIdx
                            ),indent=2))
        
        logger.info(f"Posición {positionSide} Cerrada")

    except:
        logger.error(f"Error en cerrar_posicion() {traceback.format_exc()}")
# -------------------------------

# FUNCIÓN QUE CAMBIA EL MODO DE POSICIÓN
# --------------------------------------
def cambiar_modo(category, symbol):
    try:
        bybit_session.switch_position_mode(category=category, symbol=symbol, mode=3)
    except Exception as e:
        pass
# --------------------------------------

# FUNCIÓN QUE OBTIENE EL VALOR DE LA COMISIÓN POR OPERACION
# ---------------------------------------------------------
def comision(category, symbol):
    try:
        return float(bybit_session.get_fee_rates(category=category, symbol=symbol)['result']['list'][0]['takerFeeRate'])
    except Exception as e:
        logger.error(f"ERROR EN comision()\n{e}")
        sys.exit()
# ---------------------------------------------------------

# FUNCIÓN QUE NORMALIZA LOS PRECIOS
# ---------------------------------
def normalizar_precio(category, symbol, precio):
    norma = bybit_session.get_instruments_info(category=category, symbol=symbol)['result']['list'][0]['priceFilter']['tickSize']
    redondear = len(norma.split(".")[-1])
    return round(precio, redondear)
# ---------------------------------

# Función que actualiza el grid
# -----------------------------
def actualizar_grid(category, symbol, precio_actual, distancia_grid, precio_referencia, comision):
    try:
        # variables globales y locales
        global grid, distancia_grid_actual
        
        # Generar nuevo grid por cambio de precio de referencia
        if (not(precio_referencia in grid) and precio_referencia != 0) or distancia_grid != distancia_grid_actual:
            distancia_grid_actual = distancia_grid
            grid = []
            grid.append(precio_referencia)
            distancia_grid_actual = distancia_grid
            logger.info("Generando nuevo grid...")

        distancia_grid = distancia_grid + 2*comision*100
        
        # LONG
        while grid[-1] <= precio_actual != 0:
            
            # Agregar 3 nuevos niveles al grid
            nuevo_nivel = normalizar_precio(category, symbol, grid[-1]*(1+distancia_grid/100))
            if nuevo_nivel not in grid:
                grid.append(nuevo_nivel)
            nuevo_nivel = normalizar_precio(category, symbol, grid[-1]*(1+distancia_grid/100))
            if nuevo_nivel not in grid:
                grid.append(nuevo_nivel)
            nuevo_nivel = normalizar_precio(category, symbol, grid[-1]*(1+distancia_grid/100))
            if nuevo_nivel not in grid:
                grid.append(nuevo_nivel)
            
            # Grilla actualizada
            if grid[-1] > precio_actual:
                logger.info(f"Grilla Actualizada: {grid}. Cantidad de niveles: {len(grid)}")

        # SHORT
        while grid[0] >= precio_actual != 0:
            
            # Agregar 3 nuevos niveles al grid
            nuevo_nivel = normalizar_precio(category, symbol, grid[0]/(1+distancia_grid/100))
            if nuevo_nivel not in grid:
                grid.insert(0,nuevo_nivel)
            nuevo_nivel = normalizar_precio(category, symbol, grid[0]/(1+distancia_grid/100))
            if nuevo_nivel not in grid:
                grid.insert(0,nuevo_nivel)
            nuevo_nivel = normalizar_precio(category, symbol, grid[0]/(1+distancia_grid/100))
            if nuevo_nivel not in grid:
                grid.insert(0,nuevo_nivel)
            
            # Grilla actualizada
            if grid[0] < precio_actual:
                logger.info(f"Grilla Actualizada.\n{grid}\nCantidad de niveles: {len(grid)}")
    
    except:
        logger.error(f"Error en actualizar_grid() {traceback.format_exc()}")
# -----------------------------

# hay_orden_pendiente()
#  -----------------------------------------------
def hay_orden_pendiente(ordenes_abiertas, precio, positionIdx, distancia_grid):
    try:
        for orden in ordenes_abiertas:
            if (100*abs(float(orden['price']) - precio)/precio < distancia_grid or (orden['triggerPrice'] != "" and 100*abs(float(orden['triggerPrice']) - precio)/precio < distancia_grid)) and orden['positionIdx'] == positionIdx and not orden['reduceOnly']:
                return True
    except:
        logger.error(f"Error en hay_orden_pendiente() {traceback.format_exc()}")
#  -----------------------------------------------

# hay_posicion()
#  -----------------------------------------------
def hay_posicion(ordenes_abiertas, precio, precio_tp, positionIdx, distancia_grid):
    try:
        if not hay_orden_pendiente(ordenes_abiertas, precio, positionIdx, distancia_grid):
            for orden in ordenes_abiertas:
                if 100*abs(float(orden['price']) - precio_tp)/precio_tp < distancia_grid and orden['positionIdx'] == positionIdx and orden['reduceOnly']: # Detectar TP de la posicion activa
                    return True
    except:
        logger.error(f"Error en hay_posicion() {traceback.format_exc()}")
#  -----------------------------------------------

# estrategia()
#  -----------------------------------------------
async def estrategia():
    global porc_long_actual, porc_short_actual, distancia_grid_actual, precio_referencia_actual, pausa, ordenes_abiertas
    riesgo = False
    while True:
        try:
            ti = time.time()

            # Leer parametros
            try:
                with open(f"parametros/parametros_{symbol}_{id}.json", "r") as p:
                    parametros = json.load(p)
                    leverage = round(float(parametros['apalancamiento']),2)
                    direccion = parametros['direccion'].upper()
                    porc_long = round(float(parametros['porcLong']),2)
                    porc_short = round(float(parametros['porcShort']),2)
                    distancia_grid = round(float(parametros['distanciaGrid']),2)
                    precio_referencia = float(parametros['precioReferencia'])
                    precio_objetivo = float(parametros['precioObjetivo'])
                    precio_parada = float(parametros['precioParada'])
                    ganancia_esperada = round(float(parametros['gananciaEsperada']),2)
                    max_perdida = round(float(parametros['maxPerdida']),2)
                    max_retroceso = round(float(parametros['maxRetroceso']),2)
                    proteccion_ema954 = parametros['proteccionEma954']
                    condicional_long = parametros['condicionalLong']
                    condicional_short = parametros['condicionalShort']
                    pausa = parametros['pausa']
                    reiniciar = parametros['reiniciar']

            except Exception as e:
                logger.error(f"Error leyendo los parametros {e} \nLeyendo parametros nuevamente...")
                await asyncio.sleep(0.999)

            # Evaluar riesgos
            if ((100*(patrimonio_actual-balance_inicial)/balance_inicial <= -abs(max_perdida) and max_perdida != 0) or 
                (100*(patrimonio_actual-balance_inicial)/balance_inicial > abs(ganancia_esperada) and ganancia_esperada != 0) or 
                (direccion == "LONG" and precio_actual <= precio_parada and precio_parada != 0) or
                (direccion == "LONG" and precio_actual >= precio_objetivo and precio_objetivo != 0)):
                riesgo = True
                pausa = True
                parametros['pausa'] = True
                cerrar_posicion(category, symbol, positionSide="LONG", size="")
                ordenes_abiertas = obtener_ordenes(category, symbol)
                for orden in ordenes_abiertas:
                    if orden['side'] == "Buy":
                        cancelar_orden(category, symbol, orderId=orden['orderId'])
                logger.info("ESTRATEGIA LONG DETENIDA POR GESTION DE RIESGO")
                json.dump(parametros, open("parametros.json", "w"), indent=4)
            
            if ((100*(patrimonio_actual-balance_inicial)/balance_inicial <= -abs(max_perdida) and max_perdida != 0) or 
                (100*(patrimonio_actual-balance_inicial)/balance_inicial > abs(ganancia_esperada) and ganancia_esperada != 0) or 
                (direccion == "SHORT" and precio_actual >= precio_parada and precio_parada != 0) or
                (direccion == "SHORT" and precio_actual <= precio_objetivo and precio_objetivo != 0)):
                riesgo = True
                pausa = True
                parametros['pausa'] = True
                cerrar_posicion(category, symbol, positionSide="SHORT", size="")
                ordenes_abiertas = obtener_ordenes(category, symbol)
                for orden in ordenes_abiertas:
                    if orden['side'] == "Sell":
                        cancelar_orden(category, symbol, orderId=orden['orderId'])
                logger.info("ESTRATEGIA LONG DETENIDA POR GESTION DE RIESGO")
                json.dump(parametros, open("parametros.json", "w"), indent=4)

            # Cancelar ordenes por pausa o cambio de parametros
            if pausa or distancia_grid != distancia_grid_actual or precio_referencia != precio_referencia_actual:
                ordenes_abiertas = obtener_ordenes(category, symbol)
                for orden in ordenes_abiertas:
                    if not orden['reduceOnly']:
                        cancelar_orden(category, symbol, orden['orderId'])
                distancia_grid_actual = distancia_grid
                precio_referencia_actual = precio_referencia
                
            # Verificación de Emas
            if proteccion_ema954:
                if ema9 > ema54:
                    pausa_long = False
                    pausa_short = True
                if ema9 < ema54:
                    pausa_long = True
                    pausa_short = False
            else:
                pausa_long = False
                pausa_short = False

            # Cancelar ordenes contrarias
            if direccion == "LONG" or pausa_short or porc_short != porc_short_actual:
                porc_short_actual = porc_short
                for orden in ordenes_abiertas:
                    if orden['side'] == "Sell" and not orden['reduceOnly']:
                        cancelar_orden(category, symbol, orden['orderId'])
            if direccion == "SHORT" or pausa_long or porc_long != porc_long_actual:
                porc_long_actual = porc_long
                for orden in ordenes_abiertas:
                    if orden['side'] == "Buy" and not orden['reduceOnly']:
                        cancelar_orden(category, symbol, orden['orderId'])

            # Cambiar apalancamiento
            if leverage != float(posicion[0]['leverage']):
                apalancameinto(category, symbol, leverage)
            
            # Generación del grid
            actualizar_grid(category, symbol, precio_actual, distancia_grid, precio_referencia, comision_bybit)

            # Colocar ordenes
            if not riesgo and not pausa:
                
                for nivel in grid:

                    if 0 != grid.index(nivel) != len(grid)-1:

                        # Ordenes Long
                        if not pausa_long and (direccion == "LONG" or direccion == "RANGO"):
                            positionIdx = 0 if inverso else 1
                            if not hay_orden_pendiente(ordenes_abiertas, nivel, positionIdx, distancia_grid) and not hay_posicion(ordenes_abiertas, nivel, grid[grid.index(nivel)+1], positionIdx, distancia_grid):
                                cantidad_compra = (patrimonio_actual*porc_long/100)*precio_actual if inverso else (patrimonio_actual*porc_long/100)/precio_actual
                                if nivel < precio_actual < grid[grid.index(nivel)+1]:
                                    nueva_orden(category, symbol, "LIMIT", cantidad_compra, nivel, "BUY", leverage, tp=grid[grid.index(nivel)+1])
                                if nivel > precio_actual > grid[grid.index(nivel)-1] and condicional_long:
                                    nueva_orden(category, symbol, "CONDITIONAL", cantidad_compra, nivel, "BUY", leverage, tp=grid[grid.index(nivel)+1])
                        
                        # Ordenes Short
                        if  not pausa_short and (direccion == "SHORT" or direccion == "RANGO"):
                            positionIdx = 0 if inverso else 2
                            if not hay_orden_pendiente(ordenes_abiertas, nivel, positionIdx, distancia_grid) and not hay_posicion(ordenes_abiertas, nivel, grid[grid.index(nivel)-1], positionIdx, distancia_grid):
                                cantidad_venta = (patrimonio_actual*porc_short/100)*precio_actual if inverso else (patrimonio_actual*porc_short/100)/precio_actual
                                if nivel > precio_actual > grid[grid.index(nivel)-1]:
                                    print("AQUI")
                                    nueva_orden(category, symbol, "LIMIT", cantidad_venta, nivel, "SELL", leverage, tp=grid[grid.index(nivel)-1])
                                if nivel < precio_actual < grid[grid.index(nivel)+1] and condicional_short:
                                    nueva_orden(category, symbol, "CONDITIONAL", cantidad_venta, nivel, "SELL", leverage, tp=grid[grid.index(nivel)-1])

            await asyncio.sleep(0.000999)
            #print(f"Tiempo de iteración: {time.time()-ti} \nPrecio actual: {precio_actual} \nPatrimonio: {patrimonio_actual} \n Ema54 y Ema9: {ema54}, {ema9}")

        except:
            logger.error(f"Error en estrategia(): {traceback.format_exc()}")
            await asyncio.sleep(3.6)
#  -----------------------------------------------

# Obtener credenciales
#  -----------------------------------------------
try:
    credenciales = json.load(open("credenciales.json","r"))
    api_key=credenciales['api_key']
    api_secret=credenciales['api_secret']
except:
    logger.error(f"Error obteniendo las credenciales {traceback.format_exc()}")
#  -----------------------------------------------

# Definir la session para Bybit
#  -----------------------------------------------
try:
    bybit_session = HTTP(
                        testnet=False,
                        api_key=api_key,
                        api_secret=api_secret,
                    )
except:
    logger.error(f"Error definiendo la sesión de Bybit {traceback.format_exc()}")
#  -----------------------------------------------

# Parametros iniciales
#  -----------------------------------------------
while True:
    try:
        with open("parametros_iniciales.json", "r") as p:
            parametros = json.load(p)
            inverso = parametros['inverso']
            symbol = parametros['symbol'].upper() + "USD" if inverso else parametros['symbol'].upper() + "USDT"
            leverage = round(float(parametros['apalancamiento']),2)
            direccion = parametros['direccion'].upper()
            porc_long = round(float(parametros['porcLong']),2)
            porc_short = round(float(parametros['porcShort']),2)
            distancia_grid = round(float(parametros['distanciaGrid']),2)
            precio_referencia = float(parametros['precioReferencia'])
            precio_objetivo = float(parametros['precioObjetivo'])
            precio_parada = float(parametros['precioParada'])
            ganancia_esperada = round(float(parametros['gananciaEsperada']),2)
            max_perdida = round(float(parametros['maxPerdida']),2)
            max_retroceso = round(float(parametros['maxRetroceso']),2)
            proteccion_ema954 = parametros['proteccionEma954']
            condicional_long = parametros['condicionalLong']
            condicional_short = parametros['condicionalShort']
            pausa = parametros['pausa']
            reiniciar = parametros['reiniciar']
            id = time.time()*1000
            json.dump(parametros, open(f"parametros/parametros_{symbol}_{id}.json", "w"), indent=4)
        break
    except Exception as e:
        logger.error(f"Error leyendo los parametros iniciales {e}, reintentando...")
        time.sleep(3.6)
#  -----------------------------------------------

# Variables iniciales
#  -----------------------------------------------
category = "inverse" if inverso else "linear"
patrimonio_actual = None
balance_inicial = None
porc_long_actual = porc_long
porc_short_actual = porc_short
distancia_grid_actual = distancia_grid
precio_referencia_actual = precio_referencia
grid = []
grid.append(precio_referencia)
precio_actual = 0
ordenes_abiertas = obtener_ordenes(category, symbol)
posicion = obtener_posicion(category, symbol)
comision_bybit = comision(category, symbol)
pausa_long = pausa
pausa_short = pausa
ema9 = 0
ema54 = 0

#  -----------------------------------------------

# Cambiar a modo hedege
#  -----------------------------------------------
cambiar_modo(category, symbol)
#  -----------------------------------------------

# main()
#  -----------------------------------------------
async def main():
    await asyncio.gather(patrimonio(category, symbol), precio_actual_ws(category, symbol), oredenes_ws(), estrategia(), return_exceptions=True)
#  -----------------------------------------------


# Correr el bot
if __name__ == "__main__":
    asyncio.run(main())
