from pybit.unified_trading import HTTP
import asyncio
import socket
import numpy as np
import json

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        
        # Precio actual en BYBIT
        precio = float(bybit_session.get_public_trade_history(category="linear",symbol=symbol,limit=1,)['result']['list'][0]['price'])
        return precio
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BYBIT")
        print(e)
        print("")
        return None
#--------------------------------------------------------

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Obtener el apalancamiento máximo
        max_leverage = bybit_session.get_instruments_info(category="linear", symbol=symbol)['result']['list'][0]['leverageFilter']['maxLeverage']
        return int(float(max_leverage))
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BYBIT")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN QUE CAMBIA EL APALANCAMIENTO DE UN TICK
# ------------------------------------------------------
def apalancamiento(symbol,leverage):
    try:
        
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancamiento_actual = float(bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if round(apalancamiento_actual,2) != round(float(leverage),2):
            bybit_session.set_leverage(category="linear", symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BYBIT")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE BYBIT NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancamiento_actual = float(bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if round(apalancamiento_actual,2) != round(float(leverage),2):
            bybit_session.set_leverage(category="linear", symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))

        # Definir el lado para el modo hedge
        positionSide = 0
        if side.upper() == "BUY":
            positionSide = 1
        if side.upper() == "SELL":
            positionSide = 2

        # Definir la cantidad exacta que permite el bybit
        cantidad_paso = float(bybit_session.get_instruments_info(category="linear", symbol=symbol)['result']['list'][0]['lotSizeFilter']['qtyStep'])
        quantity = round(round(quantity/cantidad_paso)*cantidad_paso, len(str(cantidad_paso).split(".")[-1]))

        # Coloca la orden "LIMIT"
        if order_type.upper() == "LIMIT":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                price=price,
                timeinforce="GTC",
                positionIdx=positionSide
            )
        
        # Coloca la orden "MARKET"
        if order_type.upper() == "MARKET":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                positionIdx=positionSide
            )

        # Coloca la orden "CONDITIONAL"
        if order_type.upper() == "CONDITIONAL":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType="MARKET",
                qty=quantity,
                price=price,
                triggerPrice=price,
                triggerBy="LastPrice",
                timeinforce="GTC",
                positionIdx=positionSide,
                triggerDirection=positionSide
            )

        order = obtener_ordenes(symbol, order["result"]["orderId"])
        #print(json.dumps(order,indent=2))
        
        if order_type.upper() == "CONDITIONAL":
            price = float(order[0]["triggerPrice"])
        else:
            price = float(order[0]["price"])
        
        print(f"\nOrden {order_type.upper()}-{side} de {order[0]['qty']} {symbol.split('USDT')[0]}  colocada en {price}. ID:", order[0]["orderId"])
        
        return {
                "orderId": order[0]["orderId"],
                "price": price,
                "qty": float(order[0]["qty"])
                }
    
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BYBIT")
        print(e)
        print("")
# ---------------------------------------------------

# FUNCION QUE MODIFICA UAN ORDEN
#--------------------------------------------------------
def modificar_orden(symbol, orderId, order_type="", quantity="", price="", side=""):
    try:

        # Definir el lado para el modo hedge
        positionSide = 0
        if side.upper() == "BUY":
            positionSide = 1
            side =side[0] + side[1:].lower()
        if side.upper() == "SELL":
            positionSide = 2
            side =side[0] + side[1:].lower()
        
        # Coloca la orden "LIMIT"
        order = bybit_session.amend_order(
            category="linear",
            symbol=symbol,
            side=side,
            orderType=order_type,
            qty=quantity,
            price=price,
            timeinforce="GTC",
            positionIdx=positionSide,
            orderId = orderId
            )

        order = obtener_ordenes(symbol, order["result"]["orderId"])
        #print(json.dumps(order,indent=2))
        
        if order_type.upper() == "CONDITIONAL":
            price = float(order[0]["triggerPrice"])
        else:
            price = float(order[0]["price"])
        
        print(f"\nOrden {order_type.upper()}-{side} de {order[0]['qty']} {symbol.split('USDT')[0]}  modificada en {price}. ID:", order[0]["orderId"])
        
        return {
                "orderId": order[0]["orderId"],
                "price": price,
                "qty": float(order[0]["qty"])
                }
    
    except Exception as e:
        print(f"\nERROR MODIFICANDO LA ORDEN EN BYBIT\n{e}")
        return None
# ---------------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol, orderId=""):
    try:
        return bybit_session.get_open_orders(category="linear",symbol=symbol,orderId=orderId)["result"]['list']

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BYBIT")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:

        if orderId == "":
            print("\nEliminando todas las ordenes...")
            bybit_session.cancel_all_orders(category="linear",symbol=symbol)
            print("\nTodas las ordenes eliminadas.")
        else:
            print(f"\nEliminando orden {orderId}...")
            bybit_session.cancel_order(category="linear",symbol=symbol,orderId=orderId)
            print("\nOrden eliminada.")

        return True
    
    except Exception as e:
        print(f"\nERROR CANCELANDO ORDEN {orderId}")
# -----------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        return bybit_session.get_positions(category="linear",symbol=symbol)["result"]["list"]

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BYBIT")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE COLOCA UN STOP LOSS
# -------------------------------
def stop_loss(symbol, positionSide, stopPrice, slSize):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            positionSide = 1
        if positionSide == "SHORT":
            positionSide = 2
        
        # Colocar la orden de Stop Loss
        if slSize == "":
            orden = bybit_session.set_trading_stop(
                                        category="linear",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Full",
                                        positionIdx=positionSide
                                    )
        else:
            orden = bybit_session.set_trading_stop(
                                        category="linear",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Partial",
                                        slSize=str(slSize),
                                        positionIdx=positionSide
                                        )
        
        createdTime = orden['time']
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if orden['orderStatus'] == "Untriggered" and 0.99*float(createdTime) <= float(orden['createdTime']) <= 1.01*float(createdTime) and orden['reduceOnly'] == True:
                
                return {
                "orderId": orden["orderId"],
                "price": orden['triggerPrice'],
                "qty": orden['qty']
                }
    
    except Exception as e:
        if "10001" in str(e):
            return "10001"
        else:
            print(f"\nERROR COLOCANDO STOP LOSS EN BYBIT\n{e}")
            return {"error": str(e)}
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type, tpSize=""):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            positionSide = 1
            side = "Sell"
            if tpSize == "":
                posiciones = obtener_posicion(symbol=symbol)
                for posicion in posiciones:
                    if posicion['positionIdx'] == positionSide:
                        tpSize = posicion['size']
        if positionSide == "SHORT":
            positionSide = 2
            side = "Buy"
            if tpSize == "":
                posiciones = obtener_posicion(symbol=symbol)
                for posicion in posiciones:
                    if posicion['positionIdx'] == positionSide:
                        tpSize = posicion['size']

        # Obtener ordenes abiertas
        ordenes_abiertas = obtener_ordenes(symbol=symbol)

        # Calcular la cantidad de TP activos
        nro_tps = 0
        for orden in ordenes_abiertas:
            if orden['stopOrderType'] == "PartialTakeProfit":
                nro_tps = nro_tps + 1
        
        if nro_tps < 20:
            if type.upper() == "MARKET":
                type = "Market"
                # Colocar Take Profit
                orden = bybit_session.set_trading_stop(
                                            category="linear",
                                            symbol=symbol,
                                            tpslMode="Partial",
                                            tpSize=str(tpSize),
                                            tpOrderType=type,
                                            positionIdx=positionSide
                                            )
            
            if type.upper() == "LIMIT":
                type = "Limit"
                # Colocar Take Profit
                orden = bybit_session.set_trading_stop(
                                            category="linear",
                                            symbol=symbol,
                                            takeProfit=str(stopPrice),
                                            tpLimitPrice=str(stopPrice),
                                            tpslMode="Partial",
                                            tpSize=str(tpSize),
                                            tpOrderType=type,
                                            positionIdx=positionSide
                                            )
        
        else:
            if type.upper() == "MARKET":
                orden = bybit_session.place_order(
                    category="linear",
                    symbol=symbol,
                    side=side,
                    orderType="MARKET",
                    qty=str(tpSize),
                    price=str(stopPrice),
                    triggerPrice=str(stopPrice),
                    triggerBy="LastPrice",
                    timeinforce="GTC",
                    positionIdx=positionSide,
                    triggerDirection=positionSide,
                    reduceOnly=True
                )

            if type.upper() == "LIMIT":
                orden = bybit_session.place_order(
                    category="linear",
                    symbol=symbol,
                    side=side,
                    orderType="Limit",
                    qty=str(tpSize),
                    price=str(stopPrice),
                    timeinforce="GTC",
                    positionIdx=positionSide,
                    reduceOnly=True
                )

        #print (json.dumps(orden, indent=2))
        createdTime = orden['time']
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if 0.99*float(createdTime) <= float(orden['createdTime']) <= 1.01*float(createdTime) and orden['orderStatus'] == "Untriggered" and orden['reduceOnly'] == True:

                return {
                "orderId": orden["orderId"],
                "price": orden['price'],
                "qty": orden['qty']
                }

        return {
        "orderId": "-",
        "price": str(stopPrice),
        "qty": str(tpSize)
        }
    
    except Exception as e:
        print("ERROR COLOCANDO TAKE PROFIT EN BYBIT")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN QUE OBTIENE EL MONTO DISPONIBLE DE LA CUENTA
# ----------------------------------------------------
def patrimonio():
    try:
        patrimonio = float(bybit_session.get_wallet_balance(accountType="UNIFIED")['result']['list'][0]['totalEquity'])

        if patrimonio != None:
            return patrimonio
        else:
            print("ERROR OBTENIENDO EL PATRIMONIO ACTUAL")
            print(patrimonio)
            print("")
    
    except Exception as e:
        print("ERROR OBTENIENDO EL PATRIMONIO ACTUAL")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CAMBIA EL MODO DE POSICIÓN
# --------------------------------------
def cambiar_modo(symbol):
    try:
        bybit_session.switch_position_mode(category="linear", symbol=symbol, mode=3)
    except Exception as e:
        pass
# --------------------------------------

# FUNCIÓN QUE OBTIENE EL VALOR DE LA COMISIÓN POR OPERACION
# ---------------------------------------------------------
def comision(symbol):
    try:
        return float(bybit_session.get_fee_rates(category="linear", symbol=symbol)['result']['list'][0]['takerFeeRate'])
    except Exception as e:
        print(f"ERROR EN comision()\n{e}")
# ---------------------------------------------------------

# FUNCION QUE VERIFICA LA CONEXION A INTERNET
# -------------------------------------------
def verificar_conexion_internet():
    try:
        # Intenta conectarse a un servidor DNS confiable (Google DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False
# -------------------------------------------

# FUNCIÓN QUE OBTINE LAS EMAs DE BYBIT
# ------------------------------------
def obtener_ema(symbol: str, interval: str = "1", periodo: int = 9, vela: int = 1) -> float:
    """
    Obtiene la EMA de un símbolo en Bybit de forma ligera y rápida.

    Parámetros:
        symbol (str): Ej. "BTCUSDT"
        interval (str): Intervalo de velas ("1","5","15","60","D", etc.)
        periodo (int): Periodo de la EMA (ej. 9, 21, 50...)
        vela (int): Índice de la vela (1 = última, 2 = penúltima, etc.)

    Retorna:
        float: Valor de la EMA en la vela especificada
    """
    try:
    
        # warm-up amplio para mayor exactitud
        need = periodo + vela + 1
        limit = max(need, 5 * periodo)
        kl = bybit_session.get_kline(category="linear", symbol=symbol, interval=interval, limit=limit)
        kl = kl.get("result", {}).get("list", [])
        kl.sort(key=lambda x: int(x[0]))
        
        closes = np.array([float(k[4]) for k in kl], dtype=float)

        if len(closes) < (periodo + vela):
            print(f"\nVelas insuficientes en la temporalidad {interval}, periodo ({periodo})")
            return None

        # EMA precisa (semilla = SMA de las primeras N)
        alpha = 2.0 / (periodo + 1.0)
        ema = np.empty_like(closes)
        ema[:] = np.nan
        first = periodo - 1
        ema[first] = closes[:periodo].mean()
        for i in range(first + 1, len(closes)):
            ema[i] = closes[i] * alpha + ema[i - 1] * (1.0 - alpha)

        return(float(ema[-vela]))

    except Exception as e:
        print(f"\nError obteniendo EMA: {e}")
        return None
# ------------------------------------

# EMA AUTOMATICA
# --------------
async def ema_auto(symbol, tipo):
    global ema_mas_cercana, ema_siguiente, ema_corretear
    correteando = False
    ultima_completada = {}
    ultima_completada['precio'] = 9999999 if tipo.upper() == "LONG" else 0
    while operar:
        try:
            
            # Obtener la ema mas cercana al precio
            # ------------------------------------
            precio_actual = precio_actual_activo(symbol)
            distancia_mas_cercana = 1
            distancia_siguiente = 1
            cercana = {}
            siguiente = {}
            for ema in emas:
                
                # Actualizar la lista de ema
                # --------------------------
                precio_ema_actual = obtener_ema(symbol, ema['temporalidad'], ema['periodo'], 1)
                if precio_ema_actual != None:
                    ema['precio'] = precio_ema_actual
                # --------------------------

                # Buscar la ema mas cercana
                # -------------------------
                # Long
                if tipo.upper() == "LONG" and ema['precio'] < precio_actual:
                    # Mas cercana
                    if abs(precio_actual-ema['precio'])/precio_actual < distancia_mas_cercana:
                        distancia_mas_cercana = abs(precio_actual-ema['precio'])/precio_actual
                        cercana = ema
                    
                    # Mayor a 1%
                    if  not ema['colocada'] and not ema['ejecutada'] and pos_size > 0 and factor*distancia_tp/100 < abs(pos_precio-ema['precio'])/pos_precio < distancia_siguiente and ema['precio'] < ultima_completada['precio']*(1-factor*distancia_tp/100):
                        distancia_siguiente = abs(pos_precio-ema['precio'])/pos_precio
                        siguiente = ema
                    
                # Short
                if tipo.upper() == "SHORT" and ema['precio'] > precio_actual:
                    # Mas cercana
                    if abs(precio_actual-ema['precio'])/precio_actual < distancia_mas_cercana:
                        distancia_mas_cercana = abs(precio_actual-ema['precio'])/precio_actual
                        cercana = ema
                    
                    # Mayor a 1%
                    if not ema['colocada'] and not ema['ejecutada'] and pos_size > 0 and  factor*distancia_tp/100 < abs(pos_precio-ema['precio'])/pos_precio < distancia_siguiente and ema['precio'] > ultima_completada['precio']*(1+factor*distancia_tp/100):
                        distancia_siguiente = abs(pos_precio-ema['precio'])/pos_precio
                        siguiente = ema
                # -------------------------            
                        
                # Verificar si se ejecuto alguna orden
                # ------------------------------------
                if disparos_limit == 0 and ema['orderId'] != "":
                    if obtener_ordenes(symbol, ema['orderId'])[0]['orderStatus'] == "Filled":
                        ema['ejecutada'] = True
                        ultima_completada = ema
                    else:
                        ema['orderId'] = ""
                        ema['orderPrice'] = ""
                        ema['colocada'] = False
                        ema['ejecutada'] = False
                # ------------------------------------

                # Reiniciar la lista de ema
                # -------------------------
                if pos_size == 0 and disparos_limit == 0:
                    ema['orderId'] = ""
                    ema['orderPrice'] = ""
                    ema['colocada'] = False
                    ema['ejecutada'] = False
                    ultima_completada['precio'] = 9999999 if tipo.upper() == "LONG" else 0
                # -------------------------
            # ------------------------------------
                
            # Emas cercana y siguiente
            # ------------------------
            ema_mas_cercana = cercana
            if ema_mas_cercana['precio'] == ultima_completada['precio']:
                 ema_mas_cercana['precio'] = obtener_ema(symbol)
            ema_siguiente = siguiente
            # ------------------------

            # Corretear la orden
            # ------------------
            if ema_corretear == {}:
                ema_corretear = ema_mas_cercana if pos_size == 0 else ema_siguiente
            if disparos_limit == 0:
                correteando = False
            if disparos_limit > 0 and ema_corretear != {} and disparo != {}:
                if not correteando:
                    print("\nCorreteando orden...")
                correteando = True
                ema_precio_actual = obtener_ema(symbol, ema_corretear['temporalidad'], ema_corretear['periodo'], 1)
                
                # Long
                if tipo.upper() == "LONG" and ema_precio_actual > disparo['precio'] and ((pos_size == 0) or (pos_size > 0 and pos_precio > ema_precio_actual and abs(ema_precio_actual-pos_precio)/pos_precio > factor*distancia_tp/100)):
                    orden = modificar_orden(symbol, disparo["orderId"], price=ema_precio_actual)
                    if orden != None:
                        for ema in emas:
                            if ema['temporalidad'] == ema_corretear['temporalidad'] and ema['periodo'] == ema_corretear['periodo']:
                                ema['orderId'] = disparo["orderId"]
                                ema['orderPrice'] = ema_precio_actual
                                ema['colocada'] = True
                                ema_corretear = ema
                                print("\n", json.dumps(ema_corretear, indent=2))
                                break
                
                # Short
                if tipo.upper() == "SHORT" and ema_precio_actual < disparo['precio'] and ((pos_size == 0) or (pos_size > 0 and pos_precio < ema_precio_actual and abs(ema_precio_actual-pos_precio)/pos_precio > factor*distancia_tp/100)):
                    orden = modificar_orden(symbol, disparo["orderId"], price=ema_precio_actual)
                    if orden != None:
                        for ema in emas:
                            if ema['temporalidad'] == ema_corretear['temporalidad'] and ema['periodo'] == ema_corretear['periodo']:
                                ema['orderId'] = disparo["orderId"]
                                ema['orderPrice'] = ema_precio_actual
                                ema['colocada'] = True
                                ema_corretear = ema
                                print("\n", json.dumps(ema_corretear, indent=2))
                                break
            # ------------------
    
            await asyncio.sleep(0.018)
        
        except Exception as e:
            print(f"\nERROR EN LA FUNCION ema_auto()\n{e}")
            await asyncio.sleep(3.6)
# --------------

# FUNCIÓN STOP AUTOMATICO
# -----------------------
async def sl_auto(symbol, tipo, perdida_usdt):
    global operar
    orderId = ""
    sl_colocado = False
    sl_100001 = False
    pos_tamaño = 0
    positionIdx = 0
    while operar:
        try:
            if verificar_conexion_internet():
                # Ordenes abiertas y posiciones
                ordenes = obtener_ordenes(symbol)
                posiciones = obtener_posicion(symbol)
                #print(json.dumps(ordenes,indent=2))

                # Precio promedio de la posición y tamaño long
                for posicion in posiciones:
                    if tipo == "LONG" and posicion['positionIdx'] == 1:
                        positionIdx = 1
                        pos_tamaño = float(posicion['size'])
                        if pos_tamaño > 0:
                            pos_precio = float(posicion['avgPrice'])
                        side = posicion['side']
                    if tipo == "SHORT" and posicion['positionIdx'] == 2:
                        positionIdx = 2
                        pos_tamaño = float(posicion['size'])
                        if pos_tamaño > 0:
                            pos_precio = float(posicion['avgPrice'])
                        side = posicion['side']

                # Aplicar SL solo si hay posicion
                if pos_tamaño > 0:
                    # Precio promedio total
                    valor_total = pos_precio*pos_tamaño
                    cantidad_total = pos_tamaño
                    precio_sl_actual = 0
                    if ordenes != []:
                        for orden in ordenes:
                            # SL actual
                            if orden['stopOrderType'] == "StopLoss" and orden['positionIdx'] == positionIdx:
                                orderId = orden['orderId']
                                precio_sl_actual = float(orden['triggerPrice'])

                            # Sumatoria
                            if not(orden['reduceOnly']) and orden['positionIdx'] == positionIdx:
                                valor_total = valor_total + float(orden['price'])*float(orden['qty'])
                                cantidad_total = cantidad_total + float(orden['qty'])

                    # Precio promedio total
                    if cantidad_total != 0:
                        precio_promedio = valor_total/cantidad_total
                        #print(json.dumps(precio_promedio_long,indent=2))

                    # Colocar SL
                    if side == "Buy":
                        positionSide = "LONG"
                        precio_sl = precio_promedio - perdida_usdt/cantidad_total
                    if side == "Sell":
                        positionSide = "SHORT"
                        precio_sl = precio_promedio + perdida_usdt/cantidad_total
                    if abs(precio_sl - precio_sl_actual)/precio_sl > 5*comision/100:
                        sl = stop_loss(symbol=symbol, positionSide=positionSide, stopPrice=precio_sl, slSize="")
                        if not("error" in sl) and not sl_colocado:
                            sl_colocado = True
                            print(f"\nStop Loss colocado en {sl['price']}")
                        if pos_tamaño == 0:
                            sl_colocado = False
                        if sl == "10001" and  not sl_100001:
                            sl_100001 = True
                            print(f"\nSL muy bajo para colocarlo en {precio_sl}")

                # Cancelar todas las ordenes pendientes después de tocar el SL
                # ------------------------------------------------------------
                if orderId != "":
                    if obtener_ordenes(symbol, orderId)[0]['orderStatus'] == "Filled":
                        operar = False
                        cancelar_orden(symbol, orderId="")
                        orderId = ""
                        print("\n😖 🔴 💥 STOP LOSS ALCANZADO 💥 🔴 😖")
                # ------------------------------------------------------------

            await asyncio.sleep(0.018)

        except Exception as e:
            print(f"ERROR EN LA FUNCION sl_auto()\n{e}")
            await asyncio.sleep(3.6)
# -----------------------

# FUNCIÓN STOP AUTOMATICO
# -----------------------
async def tp_auto(symbol, tipo, distancia_porcentual):
    global operar
    orderId = ""
    tp_colocado = False
    tamaño_pos = 0
    positionIdx = 0
    while operar:
        try:
            if verificar_conexion_internet():
                # Ordenes y posicion
                ordenes = obtener_ordenes(symbol)
                posiciones = obtener_posicion(symbol)
                for posicion in posiciones:
                    if tipo.upper() == "LONG" and posicion['positionIdx'] == 1:
                        positionIdx = 1
                        pos_side = posicion['side']
                        tamaño_pos = float(posicion['size'])
                        if tamaño_pos > 0:
                            precio_pos = float(posicion['avgPrice'])
                    if tipo.upper() == "SHORT" and posicion['positionIdx'] == 2:
                        positionIdx = 2
                        pos_side = posicion['side']
                        tamaño_pos = float(posicion['size'])
                        if tamaño_pos > 0:
                            precio_pos = float(posicion['avgPrice'])
                
                # Aplicar TP solo si hay posicion
                if tamaño_pos > 0:
                    # Buscar el TP actual
                    precio_tp_actual = 0
                    if ordenes != []:
                        for orden in ordenes:
                            if orden['stopOrderType'] == "PartialTakeProfit" and orden['positionIdx'] == positionIdx:
                                orderId = orden['orderId']
                                precio_tp_actual = float(orden['triggerPrice'])

                    # Colocar el nuevo TP
                    if pos_side == "Buy":
                        positionSide = "LONG"
                        precio_tp = precio_pos*(1 + distancia_porcentual/100)
                    if pos_side == "Sell":
                        positionSide = "SHORT"
                        precio_tp = precio_pos*(1 - distancia_porcentual/100)
                    if abs(precio_tp - precio_tp_actual)/precio_tp > 5*comision/100:
                        if orderId != "":
                            cancelar_orden(symbol, orderId)
                        tp = take_profit(symbol=symbol, positionSide=positionSide, stopPrice=precio_tp, type="LIMIT")
                        if tp != None and not tp_colocado:
                            tp_colocado = True
                            print(f"\nTake Profit colocado en {tp['price']}")
                        if tamaño_pos == 0:
                            tp_colocado = False

                # Cancelar todas las ordenes pendientes después de tocar el TP
                # ------------------------------------------------------------
                if orderId != "":
                    if obtener_ordenes(symbol, orderId)[0]['orderStatus'] == "Filled":
                        cancelar_orden(symbol, orderId="")
                        orderId = ""
                        print("\n🏆 🚀 🔥 TAKE PROFIT ALCANZADO 🔥 🚀 🏆")
                        seguir_operando = input("\n¿Seguir Operando? (SI/NO)\n->")
                        if seguir_operando.upper() == "NO" or seguir_operando.upper() == "N":
                            operar = False

                # ------------------------------------------------------------

            await asyncio.sleep(0.018)
        
        except Exception as e:
            print(f"ERROR EN LA FUNCION tp_auto()\n{e}")
            await asyncio.sleep(3.6)
# -----------------------

# FUNCIÓN CARDIACO
# -----------------
async def cardiaco(symbol, tipo, monto):
    try:
        global pos_size, pos_precio, disparos_limit, disparo, ema_corretear, ordenes_abiertas
        print("\nCardiaco iniciado")
        positionIdx = 0
        side = ""
        pos_size = 0
        pos_precio = ""
        await asyncio.sleep(1)
        
        # Definir variables
        # -----------------
        posiciones = obtener_posicion(symbol)
        for pos in posiciones:
            if pos['positionIdx'] == 1:
                if tipo.upper() == "LONG":
                    side = "Buy"
                    pos_size = float(pos['size'])
                    if pos_size> 0:
                        pos_precio = float(pos['avgPrice'])
                    positionIdx = 1
            if pos['positionIdx'] == 2:
                if tipo.upper() == "SHORT":
                    side = "Sell"
                    pos_size = float(pos['size'])
                    if pos_size> 0:
                        pos_precio = float(pos['avgPrice'])
                    positionIdx = 2
        # -----------------
   
    except Exception as e:
        print(f"\nERROR EN cardiaco()\n{e}")
    
    # Ciclo principal
    # ---------------
    conexion = True
    reconectar = False
    while operar:
        try:
            await asyncio.sleep(0.018)
            if verificar_conexion_internet():
                conexion = True
                if reconectar:
                    print("\n✅ 🛜 Conexión restablecida 🛜 ✅ ")
                    reconectar = False
                
                # Preguntar por la siguiente compra
                # ---------------------------------
                ordenes_abiertas = obtener_ordenes(symbol)
                disparos_limit = 0
                for orden in ordenes_abiertas:
                    if not orden['reduceOnly'] and orden['side'] == side:
                        disparos_limit = disparos_limit + 1
                        disparo['orderId'] = orden['orderId']
                        disparo['precio'] = float(orden['price'])
                if disparos_limit == 0:
                    print("\nColocando la próxima orden...")
                    posiciones = obtener_posicion(symbol)
                    for posicion in posiciones:
                        if posicion['positionIdx'] == positionIdx:
                            pos_size = float(posicion['size'])
                            if pos_size> 0:
                                pos_precio = float(posicion['avgPrice'])
                    ema_cercana = ema_mas_cercana if pos_size == 0 else ema_siguiente
                    if not operar:
                        ema_cercana = {}
                    if ema_cercana != {}:
                        if not ema_cercana['colocada'] and not ema_cercana['ejecutada']:
                            qty = pos_size
                            if qty == 0:
                                if ema_cercana['precio'] == 0:
                                    print(ema_cercana)
                                qty = monto/ema_cercana['precio']
                            orden = nueva_orden(symbol, "LIMIT", qty, ema_cercana['precio'], side, apalancameinto)
                            if orden != None:
                                for ema in emas:
                                    ema_cercana['colocada'] = True
                                    if ema['temporalidad'] == ema_cercana['temporalidad'] and ema['periodo'] == ema_cercana['periodo']:
                                        ema['orderId'] = orden['orderId']
                                        ema['orderPrice'] = orden['price']
                                        ema['colocada'] = True
                                        ema_corretear = ema
                                        print("\n", json.dumps(ema_corretear, indent=2))
                                        break
                    else:
                        print("\nNo encuentro donde colocar la próxima orden")
                # ---------------------------------
            
            else:
                if conexion:
                    print("\n⚠️  🛜 Problemas de conexión 🛜 ⚠️")
                    conexion = False
                    reconectar = True
        
        except Exception as e:
            print(f"\nERROR EN EL CICLO CARDIACO\n{e}")
            await asyncio.sleep(0.18)
    # ---------------
# -----------------

# FUNCIÓN PRINCIPAL
# -----------------
async def main():
    try:
        # Cambiar el modo
        # ---------------
        cambiar_modo(symbol)
        # ---------------
        
        # Correr cardiaco y la gestion de riesgo automatica
        # -------------------------------------------------
        tarea_cardiaco = asyncio.create_task(cardiaco(symbol, tipo, primera_posicion))
        tarea_sl = asyncio.create_task(sl_auto(symbol, tipo, perdida))
        tarea_ema = asyncio.create_task(ema_auto(symbol, tipo))
        
        if correr_ganancias.upper() == "S" or correr_ganancias == "SI":
            await asyncio.gather(tarea_cardiaco, tarea_sl, tarea_ema)
        else:
            tarea_tp = asyncio.create_task(tp_auto(symbol, tipo, distancia_tp))
            await asyncio.gather(tarea_cardiaco, tarea_sl, tarea_tp, tarea_ema)
        # -------------------------------------------------
    
    except Exception as e:
        print(f"\nERROR EN main()\n{e}")
# -----------------





print("\n-----------------------------------------------------------\n")
print(
    r""" ██████╗ █████╗ ██████╗ ██████╗ ██╗ █████╗  ██████╗ ██████╗ 
██╔════╝██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗██╔════╝██╔═══██╗
██║     ███████║██████╔╝██║  ██║██║███████║██║     ██║   ██║
██║     ██╔══██║██╔══██╗██║  ██║██║██╔══██║██║     ██║   ██║
╚██████╗██║  ██║██║  ██║██████╔╝██║██║  ██║╚██████╗╚██████╔╝
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ """)
print("\n-----------------------------------------------------------")
print("\n              🚀 BIENVENID@ AL CARDIACO 🚀")
print("\n   Inspirado en las estrategias de @ElGafasTrading")
print("                  🔥 ElGafas.com 🔥")

print("\n\nCOSAS IMPORTANTES QUE DEBES HACER ANTES DE USAR EL BOT:")
print("  1. Cambia a margen cruzado\n  2. Fondea al menos $50 USDT en la cuenta\n  3. Operar con cautela")

# Solicitar credenciales
# ----------------------
credenciales = False
while not credenciales:
    try:
        api_key = input("\nIntroduce tu Api Key de Bybit: \n-> ")
        api_secret = input("\nIntroduce tu Api Secret de Bybit: \n-> ")
        # ----------------------

        # Definir la session para Bybit
        # -----------------------------
        bybit_session = HTTP(
                            testnet=False,
                            api_key=api_key,
                            api_secret=api_secret,
                            )
        bybit_session.get_api_key_information()
        credenciales = True
        # -----------------------------
    except Exception as e:
        print("\n⚠️  No pude conectarme a Bybit ⚠️  Revisa tus credenciales")
# ----------------------

# Variables generales
# -------------------
capital_disponible = patrimonio()                   # Cappital de la cuenta
apalancameinto = 10                                 # Apalancamiento
comision = comision("BTCUSDT")*100                  # Comision por operacion a mercado (Suele ser la misma para cualquier par)
perdida = capital_disponible*(10-comision)/100      # Perdida en dinero del Stop Loss (USDT)
distancia_tp = 1                                    # Distancia porcentual del Take Profit (%)
capital_minimo = 50                                 # Capital minimo para Cardiaco (Montos menores incurre mayor riesgos)
ppp = 10/100                                         # Porcentaje de la primera posicion
primera_posicion = ppp*capital_disponible           # Valor en USD de la primera posicion
factor = 2                                          # Factor de distanciamiento 
# -------------------

# Verificar si el capital de la cuenta es apto para cardiaco
# -----------------------------------------------------------
operar = True
if capital_disponible < capital_minimo:
    print("\nLO SIENTO. CAPITAL MUY BAJO PARA OPERAR CARDIACO")
    print("DEBES TENER AL MENOS $50 USDT DISPONIBLES EN TU CUENTA")
    operar = False
# -----------------------------------------------------------
    
# Solicitar datos
# ---------------
# Symbol
datos_correctos = False
while not datos_correctos:
    symbol = input("\n¿Nombre del Activo, Symbol o TIck?\n-> ").upper() + "USDT"
    try:
        bybit_session.get_instruments_info(category="linear", symbol=symbol)
    except Exception as e:
        print("⚠️  No pude encontrar el nombre del activo en Bybit ⚠️")
        continue
    datos_correctos = True

# Direccion
datos_correctos = False
while not datos_correctos:
    tipo = input("\n¿Long o Short?\n-> ").upper()
    if tipo == "LONG" or tipo == "SHORT":
        datos_correctos = True
    else:
        print("⚠️. Por favor escribe 'long' o 'short' ⚠️")
        continue

# Correr ganancias
datos_correctos = False
while not datos_correctos:
    correr_ganancias = input("\n¿Correr ganancias? (Si/No)\n-> ").upper()
    if correr_ganancias.upper() == "S" or correr_ganancias == "N" or correr_ganancias == "SI" or correr_ganancias == "NO":
        datos_correctos = True
    else:
        print("⚠️. Por favor escribe 'Si' o 'No' ⚠️")
        continue

# ---------------

# Inicializar la lista de emas
# ----------------------------
emas = []
for temp in ["1", "5", "15", "60", "240", "D", "W", "M"]:
    ema9 = obtener_ema(symbol, temp, 9, 1)
    if ema9 != None:
        emas.append(
                {
                "periodo": 9,
                "temporalidad": temp,
                "precio": ema9, 
                "orderId": "", 
                "orderPrice": "",
                "colocada": False, 
                "ejecutada": False
                }
                )
    ema54 = obtener_ema(symbol, temp, 54, 1)
    if ema54 != None:
        emas.append(
                {
                "periodo": 54,
                "temporalidad": temp,
                "precio": ema54, 
                "orderId": "", 
                "orderPrice": "",
                "colocada": False, 
                "ejecutada": False
                }
                )
# --------------------------
ema_mas_cercana = {}
ema_siguiente = {}
disparo = {}
ema_corretear = {}
pos_size = 0
pos_precio = ""
disparos_limit = 1
ordenes_abiertas = 0

# Correr programa
# --------------- 
if operar:
    asyncio.run(main())
# ---------------
