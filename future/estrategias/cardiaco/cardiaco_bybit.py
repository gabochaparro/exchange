from pybit.unified_trading import HTTP
import asyncio
import socket

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
        print(f"\nERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BYBIT\n{e}")
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

        # Definir la cantidad exacta que permite el bybit
        info = bybit_session.get_instruments_info(category="linear", symbol=symbol)['result']['list'][0]
        cantidad_paso = float(info['lotSizeFilter']['qtyStep'])
        quantity = round(int(quantity/cantidad_paso)*cantidad_paso, len(str(cantidad_paso).split(".")[-1]))
        if order_type.upper() == "LIMIT" and quantity*price < 5 and price != 0:
            quantity = round(int((5.5/price)/cantidad_paso)*cantidad_paso, len(str(cantidad_paso).split(".")[-1]))
        if order_type.upper() == "MARKET":
            precio_actual = precio_actual_activo(symbol)
            if quantity*precio_actual < 5:
                quantity = round(int((5.5/precio_actual)/cantidad_paso)*cantidad_paso, len(str(cantidad_paso).split(".")[-1]))
        
        # Coloca la orden "LIMIT"
        if order_type.upper() == "LIMIT":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                price=price,
                timeinforce="GTC"
            )
        
        # Coloca la orden "MARKET"
        if order_type.upper() == "MARKET":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity
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
                triggerDirection=0
            )

        order = obtener_ordenes(symbol, order["result"]["orderId"])
        #print(json.dumps(order,indent=2))
        
        if order_type.upper() == "CONDITIONAL":
            price = float(order[0]["triggerPrice"])
        else:
            price = float(order[0]["price"])
        
        print(f"\nOrden {order_type.upper()}-{side} de {order[0]['qty']} {symbol.split('USDT')[0]}  colocada en {price}.\nID:", order[0]["orderId"])

        
        return {
                "orderId": order[0]["orderId"],
                "price": price,
                "qty": float(order[0]["qty"])
                }
    
    except Exception as e:
        print(f"\nERROR COLOCANDO LA ORDEN EN BYBIT\n{e}")
# --------------------------------------------------- 
# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:

        if orderId == "":
            print("\nEliminando todas las ordenes...")
            bybit_session.cancel_all_orders(category="linear",symbol=symbol)
            print("Todas las ordenes eliminadas.")
            print("")
        else:
            print(f"\nEliminando orden {orderId}...")
            bybit_session.cancel_order(category="linear",symbol=symbol,orderId=orderId)
            print(f"Eliminada la orden {orderId} de {symbol}.")
    
    except Exception as e:
        print(f"\nERROR CANCELANDO LA ORDEN {id} DE BYBIT\n{e}")
# -----------------------------

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
def stop_loss(symbol, positionSide, stopPrice, slSize=""):
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
                                        positionIdx=0
                                    )
        else:
            orden = bybit_session.set_trading_stop(
                                        category="linear",
                                        symbol=symbol,
                                        stopLoss=str(stopPrice),
                                        tpslMode="Partial",
                                        slSize=str(slSize),
                                        positionIdx=0
                                        )
        
        createdTime = orden['time']
        ordenes = obtener_ordenes(symbol=symbol)
        for orden in ordenes:
            if orden['orderStatus'] == "Untriggered" and 0.99*float(createdTime) <= float(orden['createdTime']) <= 1.01*float(createdTime) and orden['reduceOnly'] == True:
        
                print(f"\nStop Loss Colocado en {orden['triggerPrice']}.")
                
                return {
                "orderId": orden["orderId"],
                "price": orden['triggerPrice'],
                "qty": orden['qty']
                }
    
    except Exception as e:
        if "10001" in str(e):
            print(f"\nSL muy bajo. Bybit no puede colocarlo en {stopPrice}")
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
                    if posicion['positionIdx'] == 0:
                        tpSize = posicion['size']
        if positionSide == "SHORT":
            positionSide = 2
            side = "Buy"
            if tpSize == "":
                posiciones = obtener_posicion(symbol=symbol)
                for posicion in posiciones:
                    if posicion['positionIdx'] == 0:
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
                                            positionIdx=0
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
                                            positionIdx=0
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
                
                print(f"\nTake Profit Colocado en {orden['price']}.")

                return {
                "orderId": orden["orderId"],
                "price": orden['price'],
                "qty": orden['qty']
                }
                
        print(f"\nTake Profit Colocado en {stopPrice}.")

        return {
        "orderId": "-",
        "price": str(stopPrice),
        "qty": str(tpSize)
        }
    
    except Exception as e:
        print(f"ERROR COLOCANDO TAKE PROFIT EN BYBIT\n{e}")
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
        bybit_session.switch_position_mode(category="linear", symbol=symbol, mode=0)
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

# FUNCIÓN STOP AUTOMATICO
# -----------------------
async def sl_auto(symbol, perdida_usdt):
    orderId = ""
    sl_100001 = False
    while True:
        try:
            if verificar_conexion_internet():
                # Ordenes abiertas y posiciones
                ordenes = obtener_ordenes(symbol)
                posicion = obtener_posicion(symbol)
                #print(json.dumps(ordenes,indent=2))

                # Precio promedio de la posición y tamaño long
                if posicion[0]['size'] == "":
                    pos_tamaño = 0
                else:
                    pos_precio = float(posicion[0]['avgPrice'])
                    pos_tamaño = float(posicion[0]['size'])

                # Aplicar SL solo si hay posicion
                if pos_tamaño > 0:
                    side = posicion[0]['side']
                    # Precio promedio total
                    valor_total = pos_precio*pos_tamaño
                    cantidad_total = pos_tamaño
                    precio_sl_actual = 0
                    if ordenes != []:
                        for orden in ordenes:
                            # SL actual
                            if orden['stopOrderType'] == "StopLoss":
                                orderId = orden['orderId']
                                precio_sl_actual = float(orden['triggerPrice'])

                            # Sumatoria
                            if not(orden['reduceOnly']) and orden['side'] == side:
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
                        if not sl_100001:
                            sl = stop_loss(symbol=symbol, positionSide=positionSide, stopPrice=precio_sl, slSize="")
                            if sl == "10001":
                                sl_100001 = True

                # Cancelar todas las ordenes pendientes después de tocar el SL
                # ------------------------------------------------------------
                if orderId != "":
                    if obtener_ordenes(symbol, orderId)[0]['orderStatus'] == "Filled":
                        cancelar_orden(symbol, orderId="")
                        orderId = ""
                        print("\n😖 🔴 💥 STOP LOSS ALCANZADO 💥 🔴 😖")
                # ------------------------------------------------------------

            await asyncio.sleep(3.6)

        except Exception as e:
            print(f"ERROR EN LA FUNCION sl_auto()\n{e}")
# -----------------------

# FUNCIÓN STOP AUTOMATICO
# -----------------------
async def tp_auto(symbol, tipo, distancia_porcentual):
    orderId = ""
    if tipo.upper() == "LONG":
        tp_side = "Buy"
    if tipo.upper() == "SHORT":
        tp_side = "Sell"
    while True:
        try:
            if verificar_conexion_internet():
                # Ordenes y posicion
                ordenes = obtener_ordenes(symbol)
                posicion = obtener_posicion(symbol)
                pos_side = posicion[0]['side']
                if posicion[0]['avgPrice'] == "":
                    precio_pos = ""
                else:
                    precio_pos = float(posicion[0]['avgPrice'])
                if posicion[0]['size'] == "":
                    tamaño_pos = 0
                else:
                    tamaño_pos = float(posicion[0]['size'])
                
                # Aplicar TP solo si hay posicion
                if tamaño_pos > 0 and pos_side == tp_side:
                    # Buscar el TP actual
                    precio_tp_actual = 0
                    qty = 0
                    if ordenes != []:
                        for orden in ordenes:
                            if orden['stopOrderType'] == "PartialTakeProfit":
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
                            cancelar_orden(symbol, orderId=orderId)
                        take_profit(symbol=symbol, positionSide=positionSide, stopPrice=precio_tp, type="LIMIT")

                # Cancelar todas las ordenes pendientes después de tocar el TP
                # ------------------------------------------------------------
                if orderId != "":
                    if obtener_ordenes(symbol, orderId)[0]['orderStatus'] == "Filled":
                        cancelar_orden(symbol, orderId="")
                        orderId = ""
                        print("\n🏆 🚀 🔥 TAKE PROFIT ALCANZADO 🔥 🚀 🏆")
                # ------------------------------------------------------------

            await asyncio.sleep(3.6)
        
        except Exception as e:
            print(f"ERROR EN LA FUNCION tp_auto()\n{e}")
# -----------------------

# FUNCIÓN CARDIACO
# -----------------
async def cardiaco(symbol, tipo, precio, monto):
    print("\nCardiaco iniciado")
    
    # Definir variables
    # -----------------
    if tipo == "LONG":
        side = "BUY"
    if tipo == "SHORT":
        side = "SELL"
    # -----------------

    # Colocar primera orden
    # ---------------------
    if obtener_posicion(symbol)[0]['size'] == "0" and disparos == 0:
        qty = monto/precio
        print("\nColocando la primera orden . . .")
        nueva_orden(symbol, "LIMIT", qty, precio, side, apalancameinto)
    # ---------------------

    # Ciclo principal
    # ---------------
    conexion = True
    reconectar = False
    if tipo.upper() == "LONG":
        side = "Buy"
    if tipo.upper() == "SHORT":
        side = "Sell"
    while True:
        try:
            if verificar_conexion_internet():
                conexion = True
                if reconectar:
                    print("\n✅ 🛜 Conexión restablecida 🛜 ✅ ")
                    reconectar = False
                
                # Preguntar por la siguiente compra
                # ---------------------------------
                ordenes = obtener_ordenes(symbol)
                disparos_limit = 0
                for orden in ordenes:
                    if not orden['reduceOnly'] and orden['side'] == side:
                        disparos_limit = disparos_limit + 1
                if disparos_limit == 0:
                    precio = ""
                    posicion = obtener_posicion(symbol)[0]
                    qty_posicion = posicion['size']
                    if qty_posicion == "":
                        qty = 0
                    else:
                        qty = float(qty_posicion)
                    await asyncio.sleep(3.6)
                    datos_correctos = False
                    orden = "compra" if tipo == "LONG" else "venta"
                    while not datos_correctos:
                        try:
                            precio = float(await asyncio.to_thread(input, f"\n¿Precio de la siguiente {orden}?\n('0' para disparar a mercado)\n-> "))
                        except Exception as e:
                            print("⚠️  Ingresa un número válido ⚠️")
                            continue
                        datos_correctos = True
                    if precio != 0:
                        if qty == 0:
                            qty = monto/precio
                        nueva_orden(symbol, "LIMIT", qty, precio, side, apalancameinto)
                    if precio == 0:
                        if qty == 0:
                            qty = monto/precio_actual_activo(symbol)
                        nueva_orden(symbol, "MARKET", qty, 1, side, apalancameinto)
                # ---------------------------------
            
            else:
                if conexion:
                    print("\n⚠️  🛜 Problemas de conexión 🛜 ⚠️")
                    conexion = False
                    reconectar = True
            
            await asyncio.sleep(3.6)
        
        except Exception as e:
            print(f"\nERROR EN EL CICLO PRINCIPAL\n{e}")
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
        tarea_cardiaco = asyncio.create_task(cardiaco(symbol, tipo, precio, primera_posicion))
        tarea_sl = asyncio.create_task(sl_auto(symbol, perdida))
        
        if correr_ganancias.upper() == "S" or correr_ganancias == "SI":
            await asyncio.gather(tarea_cardiaco, tarea_sl)
        else:
            tarea_tp = asyncio.create_task(tp_auto(symbol, tipo, distancia_tp))
            await asyncio.gather(tarea_cardiaco, tarea_sl, tarea_tp)
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
        api_key = "1XJt60yrfh4sSwU45Q" #input("\nIntroduce tu Api Key de Bybit: \n-> ")
        api_secret = "GyQyHOe8SRKje2g4WN7JxEZrfIqy0sOqtjdP" #input("\nIntroduce tu Api Secret de Bybit: \n-> ")
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
ppp = 10/100                                        # Porcentaje de la primera posicion
primera_posicion = ppp*capital_disponible           # Valr en USD de la primera posicion
# -------------------

# Verificar si el capital de la cuenta es apato para cardiaco
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
    correr_ganancias = input("\n¿Correr ganancias, (Si/No)?\n-> ").upper()
    if correr_ganancias.upper() == "S" or correr_ganancias == "N" or correr_ganancias == "SI" or correr_ganancias == "NO":
        datos_correctos = True
    else:
        print("⚠️. Por favor escribe 'Si' o 'No' ⚠️")
        continue

# Precio
ordenes = obtener_ordenes(symbol)
disparos = 0
datos_correctos = False
precio = 0
for orden in ordenes:
    if not orden['reduceOnly']:
        disparos = disparos + 1
orden = "compra" if tipo == "LONG" else "venta"
if obtener_posicion(symbol)[0]['size'] == "0" and disparos == 0:
    while not datos_correctos:
        try:
            precio = float(input(f"\n¿Precio de la primera {orden}?\n-> "))
        except Exception as e:
            print("⚠️  Ingresa un número válido ⚠️")
            continue
        datos_correctos = True
# ---------------

# Correr programa
# --------------- 
if operar:
    asyncio.run(main())
# ---------------
