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
        return 0
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

# FUNCIÓN DE BYBIT NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage, tp=0.0, sl=0.0):
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

        tpOrderType = "Market"
        if tp > 0:
            tpOrderType = "Limit"

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
                category="linear",
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
                triggerDirection=positionSide,
                tpslMode = "Partial",
                tpOrderType = tpOrderType,
                takeProfit = str(tp),
                tpLimitPrice = str(tp),
                stopLoss = str(sl)
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
        print(f"\nERROREN LA FUNCION nueva_orden()\n{e}")
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

# FUNCION QUE MODIFICA UAN ORDEN
#--------------------------------------------------------
def modificar_orden(symbol, orderId, quantity="", price="", tp="", sl=""):
    try:
        
        # Coloca la orden "LIMIT"
        order = bybit_session.amend_order(
            category="linear",
            symbol=symbol,
            qty=quantity,
            price=price,
            timeinforce="GTC",
            orderId = orderId,
            takeProfit = str(tp),
            tpLimitPrice = str(tp),
            stopLoss = str(sl)
            )

        order = obtener_ordenes(symbol, order["result"]["orderId"])
        #print(json.dumps(order,indent=2))
        
        price = float(order[0]["price"])
        
        print(f"\nOrden de {order[0]['qty']} {symbol.split('USDT')[0]}  modificada en {price}. ID:", order[0]["orderId"])
        
        return {
                "orderId": order[0]["orderId"],
                "price": price,
                "qty": float(order[0]["qty"])
                }
    
    except Exception as e:
        print(f"\nERROR MODIFICANDO LA ORDEN EN BYBIT\n{e}")
# ---------------------------------------------------

# FUNCION PARA SOLICITAR LAS CREDENCIALES DE CUALQUIER EXCHANGE
# -------------------------------------------------------------
def solicitar_credenciales(exchange: str, debug: bool =False):
    credenciales = False
    
    # Solicitar credenciales de Bybit
    # -------------------------------
    if exchange.upper() == "BYBIT":
        while not credenciales:
            try:
                from pybit.unified_trading import HTTP
                
                # Solicitar credenciales
                # ----------------------
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
                return bybit_session
                # -----------------------------
            except Exception as e:
                print("\n⚠️  No pude conectarme a Bybit ⚠️  Revisa tus credenciales")
                if debug:
                    print(f"\n{e}")
        # -------------------------------
    
    # Solicitar credenciales de Binance
    # -------------------------------
    if exchange.upper() == "BINANCE":
        while not credenciales:
            try:
                from binance.client import Client
                
                # Solicitar credenciales
                # ----------------------
                api_key = input("\nIntroduce tu Api Key de Binance: \n-> ")
                api_secret = input("\nIntroduce tu Api Secret de Binance: \n-> ")
                # ----------------------

                # Definir el cliente para Binance
                # -------------------------------
                binance_client = Client(
                                            api_key=api_key,
                                            api_secret=api_secret,
                                            tld="com"
                                        )
                binance_client.get_account_api_permissions()
                credenciales = True
                return binance_client
                # -------------------------------
            except Exception as e:
                print("\n⚠️  No pude conectarme a Binance ⚠️  Revisa tus credenciales")
                if debug:
                    print(f"\n{e}")
        # -------------------------------
# -------------------------------------------------------------

# FUNCIÓN QUE OBTINE LAS EMAs DE BYBIT
# ------------------------------------
def obtener_ema_bybit(symbol: str, interval: str = "1", periodo: int = 9, vela: int = 1) -> float:
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
        from pybit.unified_trading import HTTP
        import numpy as np

        # Definir la session para Bybit
        # -----------------------------
        bybit_session = HTTP(
                            testnet=False,
                            api_key="",
                            api_secret="",
                            )
    
        # warm-up amplio para mayor exactitud
        need = periodo + vela + 1
        limit = max(need, 5 * periodo)
        kl = bybit_session.get_kline(category="linear", symbol=symbol, interval=interval, limit=limit)
        kl = kl.get("result", {}).get("list", [])
        kl.sort(key=lambda x: int(x[0]))
        
        closes = np.array([float(k[4]) for k in kl], dtype=float)

        if len(closes) < (periodo + vela):
            raise ValueError(f"Velas insuficientes: {len(closes)} < {periodo + vela}")

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

# FUNCIÓN QUE DETERMINA DONDE COLOCAR LA ORDEN CON CON TP Y SL
# ------------------------------------------------------------
def ema954(symbol: str, direccion: str, periodo: int, temporalidad: int, distancia_sl: float, riesgo_sl: float, debug: bool = True):
        
        try:
            import time

            # Variables iniciales
            # -------------------
            side = "BUY" if direccion == "LONG" else "SELL"
            posicion_detectada = False
            precio_ema = obtener_ema_bybit(symbol=symbol, interval=temporalidad, periodo=periodo, vela=1)
            esperando_entrada = False
            # -------------------
                
            # Capital de la cuenta
            # --------------------
            capital = patrimonio()
            qty = capital*(riesgo_sl/distancia_sl)/precio_actual_activo(symbol)
            # --------------------
        
        except Exception as e:
            if debug:
                print(f"\nERROR EN LA FUNCION ema954()\n{e}")
        
        while True:
            try:
                # Obtener posicion
                # ----------------
                positionIdx = 1 if direccion == "LONG" else 2
                posiciones = obtener_posicion(symbol)
                for pos in posiciones:
                    if pos['positionIdx'] == positionIdx:
                        pos_size = float(pos['size'])
                # ----------------

                # Precio actual ema
                # -----------------
                precio_ema_actual = obtener_ema_bybit(symbol=symbol, interval=temporalidad, periodo=periodo, vela=1)
                precio_ema_actual = precio_ema_actual*1.0018 if direccion == "LONG" else precio_ema_actual*0.9982
                # -----------------
                
                # Gestion Long
                # ------------
                factor = 2.01
                if direccion.upper() == "LONG":
                    precio_sl = precio_ema_actual*(1-distancia_sl/100)
                    precio_tp = precio_ema_actual*(1+factor*distancia_sl/100)
                # ------------
                
                # Gestion Short
                # -------------
                if direccion.upper() == "SHORT":
                    precio_sl = precio_ema_actual*(1+distancia_sl/100)
                    precio_tp = precio_ema_actual*(1-factor*distancia_sl/100)
                # -------------

                # Colocar o modificar la orden
                # ----------------------------
                precio_actual = precio_actual_activo(symbol)
                if pos_size == 0:
                    posicion_detectada = False
                    if len(obtener_ordenes(symbol)) == 0:
                        if (direccion == "LONG" and precio_actual > precio_ema_actual) or (direccion == "SHORT" and precio_actual < precio_ema_actual):
                            nueva_orden(symbol, "LIMIT", qty, precio_ema_actual, side, 10, precio_tp, precio_sl)
                            esperando_entrada = False
                        else:
                            if not esperando_entrada:
                                esperando_entrada = True
                                print("\nEsperando nueva entrada...")
                    else:
                        orderId = obtener_ordenes(symbol)[0]['orderId']
                        if (direccion == "LONG" and precio_ema_actual > precio_ema) or (direccion == "SHORT" and precio_ema_actual < precio_ema):
                            modificar_orden(symbol, orderId, price=precio_ema_actual, tp=precio_tp, sl=precio_sl)
                            precio_ema = precio_ema_actual
                else:
                    if not posicion_detectada:
                        print("\nPosición activa")
                        posicion_detectada = True
                        esperando_entrada = False
                # ----------------------------

                # Tiempo de espera
                # ----------------
                time.sleep(3.6)
                # ----------------

            except Exception as e:
                if debug:
                    print(f"\nERROR EN EL CICLO ema954()\n{e}")
# ------------------------------------------------------------

# FUNCIÓN PRINCIPAL
# -----------------
def main(debug=False):
    try:
        global bybit_session
        
        # Solicitar credenciales
        # ----------------------
        bybit_session = solicitar_credenciales("BYBIT")
        # ----------------------

        # Solicitar parametros
        # --------------------
        # Symbol
        dato_correcto = False
        while not dato_correcto:
            symbol = input("\n¿Nombre del Activo, Symbol o TIck?\n-> ").upper() + "USDT"
            try:
                bybit_session.get_instruments_info(category="linear", symbol=symbol)
            except Exception as e:
                print("⚠️  No pude encontrar el nombre del activo en Bybit ⚠️")
                continue
            dato_correcto = True

        # Direccion
        dato_correcto = False
        while not dato_correcto:
            direccion = input("\n¿Long o Short?\n-> ").upper()
            if direccion == "LONG" or direccion == "SHORT":
                dato_correcto = True
            else:
                print("⚠️. Por favor escribe 'long' o 'short' ⚠️")
                continue

        # Ema
        dato_correcto = False
        while not dato_correcto:
            try:
                periodo = int(input("\n¿Ema de 9 o 54?\n-> "))
                if periodo == 9 or periodo == 54:
                    dato_correcto = True
                else:
                    1/0
                temporalidad = int(input("\n¿Temporalidad? (1 = 1min, 5 = 5min, 15 = 15 min)\n-> "))
            except Exception as e:
                print("\n⚠️  Introduce el número 1, 5 o 15 ⚠️")

        # Distancia SL
        dato_correcto =False
        while not dato_correcto:
            try:
                distancia_sl = float(input("\n¿Distancia del Stop Loss (%)?\n-> "))
                dato_correcto = True
            except Exception as e:
                print("\n⚠️  Introduce un valor válido ⚠️")

        # Riesgo del SL
        dato_correcto =False
        while not dato_correcto:
            try:
                riesgo_sl = float(input("\n¿Riesgo a correr? (%)\n-> "))
                dato_correcto = True
            except Exception as e:
                print("\n⚠️  Introduce un valor válido ⚠️")
        # --------------------

        cambiar_modo(symbol)
        ema954(symbol, direccion, periodo, temporalidad, distancia_sl, riesgo_sl, debug=True)

    except Exception as e:
        if debug:
            print(f"\nERROR EN main()\n{e}")
# -----------------

# Correr el programa principal
# ----------------------------
main(debug=True)
# ----------------------------