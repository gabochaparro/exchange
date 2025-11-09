# Importar librerias
try:
    import asyncio, aiohttp, json, hmac, hashlib, time, os, logging, sys, traceback
    from urllib.parse import urlencode
    from binance.cm_futures import CMFutures
except Exception as e:
    print(f"\nERROR EXPORTANDO LIBRERIAS: {e}")
    sys.exit()

# Capturar errores no manejados
try:
    # Configurar logging
    def configurar_logging(archivo: str = "app.log", debug: bool = False):
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
            import traceback
            print(f"\nERROR CONFIGURANDO LOGGING: {traceback.format_exc()}")

    logger = configurar_logging()

    # Capturar errores no controlados (tracebacks)
    def registrar_excepciones(exc_type, exc_value, exc_traceback):
        tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(tb)
        
    # Ejecuta registrar_excepciones() cada vez que ocurre un error no manejado 
    sys.excepthook = registrar_excepciones
except:
    print(f"\nERROR EN LA CAPTURA DE ERRORES NO MANEJADOS:\n{traceback.format_exc()}")
    sys.exit()

# Obtener credenciales
credenciales = json.load(open("credenciales.json","r"))

binance_client = CMFutures(
                            key=credenciales['api_key'],
                            secret=credenciales['api_secret']
                            )

# FUNCIONES PARA BINANCE
API_KEY = os.getenv("API_KEY", credenciales['api_key'])
API_SECRET = os.getenv("API_SECRET", "u5ZlU1SZfuYPxkxB8590tyYsVN8RaJawgvb8jhyRbOofVBSeHMYBdyi0nOlw3KOW")
BASE = "https://dapi.binance.com"
HEAD = {"X-MBX-APIKEY": API_KEY}
USER_WS = "wss://dstream.binance.com/ws"
TRADE_WS = "wss://dstream.binance.com/ws-api/v3"
MARKET_WS = "wss://dstream.binance.com/ws"  # streams de mercado
SYMBOL = "BNBUSD_PERP"
session = None
orden = False


# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Acondicionar el symbol
        symbol = symbol.upper()

        # Obtener el apalancamiento máximo
        brackets = binance_client.leverage_brackets(pair=symbol)
        for bracket in brackets:
            if bracket['symbol'] == symbol:
                return bracket['brackets'][0]['initialLeverage']
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BINANCE")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN QUE CAMBIA EL APALANCAMIENTO DE UN TICK
# ------------------------------------------------------
def apalancameinto(symbol,leverage):
    try:
        
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        binance_client.change_leverage(symbol=symbol, leverage=int(leverage))
    
    except Exception as e:
        print(f"ERROR CAMBIANDO EL APALANCAMIENTO DE {symbol} EN BINANCE")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE BINANCE NUEVA ORDEN 'LIMIT' , 'MARKET' o "CONDITIONAL"
# -----------------------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        # Cambia el apalancamiento
        max_leverage = apalancameinto_max(symbol=symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        apalancameinto(symbol=symbol, leverage=leverage)

        # Define el lado para el modo hedge
        if side == "BUY":
            position_side = "LONG"
        if side == "SELL":
            position_side = "SHORT"

        # Definir la cantidad exacta que permite binance
        orden = binance_client.exchange_info()['symbols']
        for activo in orden:
            if activo['symbol'] == symbol:
                cantidad_paso = float(activo['filters'][1]['stepSize'])
        quantity = round(quantity/cantidad_paso)*cantidad_paso

        # Coloca la orden "LIMIT" , "MARKET" o "CONDITIONAL"
        if order_type == "LIMIT":
            order = binance_client.new_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=order_type,
                quantity=quantity,
                price=price,
                timeinforce="GTC",
                recvWindow=int(time.time()*1000),
            )
        if order_type == "MARKET":
            order = binance_client.new_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=order_type,
                quantity=quantity,
                recvWindow=int(time.time()*1000)
            )
        if order_type == "CONDITIONAL":
            order = binance_client.new_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type="STOP_MARKET",
                quantity=quantity,
                stopPrice=price,
                timeinforce="GTC",
                recvWindow=int(time.time()*1000),
            )
        #print(json.dumps(order,indent=2))
        print(f"Orden colocada en {order['price']}. ID:", order["orderId"])
        print((""))
        
        if order_type == "CONDITIONAL":
            price = order["stopPrice"]
        else:
            price = order["price"]

        return {
                "orderId": order["orderId"],
                "price": price,
                "qty": order["origQty"]
                }

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BINANCE")
        print(e)
        print("")
# -----------------------------------------------------------------

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:

        print("Cancelando todas las ordenes abiertas...")
        binance_client.cancel_open_orders(symbol=symbol, recvWindow=int(time.time()*1000))
        print("Ordenes abiertas canceladas")
        print("")
    
    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BINANCE")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        return binance_client.get_orders(symbol=symbol)

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS")
        print(e)
        print("")
        return []
# ----------------------------------------------------

# FUNCIÓN QUE BUSCA LA INFO DE TODAS LAS ORDENES CERRADAS
# -------------------------------------------------------
def obtener_historial_ordenes(symbol,limit=100):
    try:

        # Definir el limite de ordenes a buscar
        if limit > 100:
            limit = 100

        return binance_client.get_all_orders(symbol=symbol,limit=limit)
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN obtener_historial_ordenes() de BINANCE")
        print(e)
        print("")
# -------------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:

        print(f"Cancelando orden {orderId}")
        order = binance_client.cancel_order(symbol=symbol, orderId=orderId)
        print(f"Eliminada la orden {orderId} de {symbol.split('USD')[0]}.")
        print("")
        return order
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {id} DE BINANCE")
        print(e)
        print("")
# -----------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        posiciones = binance_client.get_position_risk(symbol=symbol)
        #print(json.dumps(posiciones,indent=2))
        lista = []
        for posicion in posiciones:
            if posicion['symbol'] == symbol and posicion['positionAmt'] != "0":
                lista.append(posicion)
        return lista

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BINANCE")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(symbol, positionSide):
    try:

        # Obtener posiciones
        posiciones = obtener_posicion(symbol)
        
        # Definir el lado segun la posición
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "SELL"
        if positionSide == positionSide.upper():
            side = "BUY"

        for posicion in posiciones:
            if posicion['positionSide'] == positionSide.upper():
                quantity = abs(float(posicion['positionAmt']))
                print(quantity)
            
        # Cerrar posición
        print("Cerrando posición...")
        order = binance_client.new_order(
                                    symbol=symbol, 
                                    side=side, 
                                    positionSide=positionSide, 
                                    type="MARKET",
                                    quantity=quantity, 
                                    timestamp=int(time.time()*1000)
                                    )
        print(f"Posición {positionSide} Cerrada")
        print("")
        return order

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BINANCE")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type, tpSize=""):
    try:

        # Definir parametros
        positionSide = positionSide.upper()
        type = type.upper()
        if positionSide == "LONG":
            side = "SELL"
            quantity = str(tpSize)
            if tpSize == "":
                quantity = obtener_posicion(symbol=symbol)[0]['positionAmt']
        if positionSide == "SHORT":
            side = "BUY"
            quantity = str(tpSize)
            if tpSize == "":
                quantity = obtener_posicion(symbol=symbol)[1]['positionAmt']

        info = binance_client.exchange_info()['symbols']
        for data in info:
            if data['symbol'] == symbol:
                decimales_precio = len(data['filters'][0]['tickSize'].split(".")[-1])
                tickSize = float(data['filters'][0]['tickSize'])
                stopPrice = round(round(float(stopPrice)/tickSize)*tickSize, decimales_precio)
                decimales_moneda = len(data['filters'][1]['stepSize'].split(".")[-1])
                stepSize = float(data['filters'][1]['stepSize'])
                quantity = round(round(float(quantity)/stepSize)*stepSize,decimales_moneda)
                print("precio:", stopPrice, "cantidad:", quantity)

        # Colocar Take Profit Market
        if type == "MARKET":
            type = "TAKE_PROFIT_MARKET"
            orden = binance_client.new_order(
                                            symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide, 
                                            type=type, 
                                            stopPrice=float(stopPrice), 
                                            closePosition=True,
                                            timestamp = int(time.time()*1000)
                                            )
        
        # Colocar Take Profit Limit
        if type == "LIMIT":
            type = "TAKE_PROFIT"
            orden = binance_client.new_order(
                                            symbol=symbol, 
                                            side=side, 
                                            positionSide=positionSide, 
                                            type=type, 
                                            stopPrice=float(stopPrice),
                                            price=float(stopPrice),
                                            quantity=quantity,
                                            timestamp = int(time.time()*1000)
                                            )
        
        print(f"Take Profit Colocado en {orden['stopPrice']}. ID:", orden["orderId"])
        print("")
        
        return {
                "orderId": orden["orderId"],
                "price": orden["stopPrice"],
                "qty": orden["origQty"]
                }
    
    except Exception as e:
        print("ERROR COLOCANDO TAKE PROFIT EN BINANCE")
        print(e)
        print("")
# ------------------------------------------------

# ------------------- AUTH -------------------
def sign(params: dict) -> dict:
    """Firma parámetros para Binance REST API (Coin-M Futures)"""
    # Eliminar valores None
    params = {k: v for k, v in params.items() if v is not None}

    # Crear query ordenada y codificada
    query = urlencode(params, doseq=True)
    signature = hmac.new(API_SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()

    # Agregar firma al diccionario
    params["signature"] = signature
    return params

# ------------------- OBTENER LISTEN KEY -------------------
async def get_key(session):
    async with session.post(f"{BASE}/dapi/v1/listenKey", headers=HEAD) as r:
        j = await r.json()
        if r.status != 200: raise SystemExit(j)
        logger.info(f"🔑 ListenKey: {j['listenKey']}")
        return j["listenKey"]
    
# ------------------- STREAM DE USUARIO -------------------
async def user_stream(session):
    key = await get_key(session)
    async with session.ws_connect(f"{USER_WS}/{key}") as ws:
        logger.info("✅ Conectado al stream de usuario")
        async for msg in ws:
            data = json.loads(msg.data)
            # Detectar las ejecuciones aqui y colocar los TPs
            logger.info(data)

# ------------------- STREAM DE MERCADO -------------------
async def market_stream(session, symbol):
    symbol = symbol.lower()
    async with session.ws_connect(f"{MARKET_WS}/{symbol}@aggTrade") as ws:
        logger.info(f"📈 Suscrito a {symbol}@aggTrade")
        async for msg in ws:
            data = json.loads(msg.data)
            await on_tick(data=data)

# ------------------- MANTENER VIVO -------------------
async def keepalive(session):
    while True:
        await asyncio.sleep(1800)
        await session.put(f"{BASE}/dapi/v1/listenKey", headers=HEAD)
        logger.info("🔄 Keepalive enviado")

# ------------------- MAIN -------------------
async def main():
    while True:
        global session
        try:
            session = aiohttp.ClientSession()
            await asyncio.gather(user_stream(session), market_stream(session, SYMBOL), keepalive(session))
        except:
            logger.error(f"Error en main(): {traceback.format_exc()}")
            await session.close()
            logger.info("Iniciando una nueva sesión...")
            await asyncio.sleep(9.9)

# ------------------- ON TICK -------------------
async def on_tick(data):
    # Ejecutar cualquier logica aquí
    print("\n", data)
    global orden
    if not orden:
        take_profit(SYMBOL, "LONG", 1999, "LIMIT", 54)
        orden = True
    await asyncio.sleep(1)

# ------------------- ENTRY -------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⛔ Finalizado manualmente")

