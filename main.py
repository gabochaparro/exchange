import okx.Account
import okx.PublicData
import okx.Trade
import credenciales
from binance.client import Client
from pybit.unified_trading import HTTP
import pybitget
import okx
import kucoin_futures.client
from gate_api import ApiClient, Configuration, FuturesApi, FuturesOrder
import json
import time


# Definir el cliente para Binance
binance_client = Client(
                            api_key=credenciales.binance_api_key,
                            api_secret=credenciales.binance_api_secret,
                            tld="com"
                        )

# Definir la session para Bybit
bybit_session = HTTP(
                    testnet=False,
                    api_key=credenciales.bybit_api_key,
                    api_secret=credenciales.bybit_api_secret,
                )

# Definir el cliente para BitGet
bitget_client = pybitget.Client(
                            api_key=credenciales.bitget_api_key, 
                            api_secret_key=credenciales.bitget_api_secret, 
                            passphrase = credenciales.bitget_api_passphrase, 
                            use_server_time=False,
                        )

# Definir la API de OKX
tradeAPI = okx.Trade.TradeAPI(credenciales.okx_api_key, 
                              credenciales.okx_api_secret, 
                              credenciales.okx_api_passphrase, 
                              False, 
                              "0"
                              )
accountAPI = okx.Account.AccountAPI(credenciales.okx_api_key, 
                              credenciales.okx_api_secret, 
                              credenciales.okx_api_passphrase, 
                              False, 
                              "0"
                              )

# Definir la API de KuCoin
kucoin_client = kucoin_futures.client.Trade(
                                            key=credenciales.kucoin_api_key, 
                                            secret=credenciales.kucoin_api_secret, 
                                            passphrase=credenciales.kucoin_api_passphrase
                                            )

# Definir la API de GATE.io
# Configuración
config = Configuration(
    key=credenciales.gateio_api_key,  # Reemplaza con tu API key
    secret=credenciales.gateio_api_secret  # Reemplaza con tu API secret
)
# Creación del cliente
with ApiClient(config) as api_client:
    futures_api = FuturesApi(api_client)


# FUNCIÓN QUE DEFINE EL SYMBOL SEGUN EL EXCHANGE
# ----------------------------------------------
def definir_symbol(exchange, symbol):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()

        if exchange == "BINANCE" or exchange.upper() == "BYBIT":
            symbol = symbol + "USDT"
        
        if exchange == "BITGET":
            symbol = symbol + "USDT_UMCBL"

        if exchange == "BINGX":
            symbol = symbol + "-USDT"

        if exchange == "OKX":
            symbol = symbol + "-USDT-SWAP"
        
        if exchange == "KUCOIN":
            symbol = symbol + "USDTM"
        
        if exchange == "GATEIO":
            symbol = symbol + "_USDT"
 
        return symbol
    
    except Exception as e:
        print("ERROR EN LA DEFICIÓN DEL SÍMBOLO")
# ----------------------------------------------

# FUNCIÓN DE BINANCE NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------------
def binance_nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        # Cambia el apalancamiento
        binance_client.futures_change_leverage(symbol=symbol, leverage=leverage)

        # Define el lado para el modo hedge
        if side == "BUY":
            position_side = "LONG"
        if side == "SELL":
            position_side = "SHORT"

        # Coloca la orden "LIMIT" o "MARKET"
        if order_type == "LIMIT":
            order = binance_client.futures_create_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=order_type,
                quantity=quantity,
                price=price,
                timeinforce="GTC",
                timestamp=time.time()
            )
        if order_type == "MARKET":
            order = binance_client.futures_create_order(
                symbol=symbol,
                side=side,
                positionSide=position_side,
                type=order_type,
                quantity=quantity,
                timestamp=time.time()
            )
        print(f"Orden colocada en {order["price"]}. ID:", order["orderId"])
        print((""))
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BINANCE")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE BYBIT NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------------
def bybit_nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        # Cambia el apalancamiento
        apalancamiento_actual = (bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
        #print("apalancamiento actual:", apalancamiento_actual)
        if apalancamiento_actual != str(leverage):
            bybit_session.set_leverage(category="linear", symbol=symbol, buyLeverage=str(leverage),sellLeverage=str(leverage))
            apalancamiento_actual = (bybit_session.get_positions(category="linear", symbol=symbol)["result"]["list"][0]["leverage"])
            #print("apalancamiento actual:", apalancamiento_actual)

        # Definir el lado para el modo hedge
        if side == "BUY":
            positionSide = 1
        if side == "SELL":
            positionSide = 2

        # Coloca la orden "LIMIT" o "MARKET"
        if order_type == "LIMIT":
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
        if order_type == "MARKET":
            order = bybit_session.place_order(
                category="linear",
                symbol=symbol,
                side=side[0] + side[1:].lower(),
                orderType=order_type,
                qty=quantity,
                positionIdx=positionSide
            )
        print(f"Orden colocada en {price}. ID:", order["result"]["orderId"])
        print("")
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BYBIT")
        print(e)
        print("")
# ---------------------------------------------------

# FUNCIÓN DE BITGET NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def bitget_nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:

        # Modificar apalancamiento
        bitget_client.mix_adjust_leverage(symbol=symbol, marginCoin="USDT", leverage=leverage, holdSide=None)

        # Definir el lado
        if side == "BUY":
            side = "OPEN_LONG"
        if side == "SELL":
            side = "OPEN_SHORT"

        # Colocar la orden
        order = bitget_client.mix_place_order(
                                        symbol=symbol, 
                                        marginCoin="USDT", 
                                        size=quantity,
                                        side=side, 
                                        orderType=order_type, 
                                        price=price
                                    )
        
        print(f"Orden colocada en {price}. ID:", order["data"]["orderId"])
        print("")

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BITGET")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN DE BINGX NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def bingx_nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:

        if side == "BUY":
            positionSide = "LONG"
        if side == "SELL":
            positionSide = "SHORT"

        import requests
        import hmac
        from hashlib import sha256

        APIURL = "https://open-api.bingx.com"
        APIKEY = credenciales.bingx_api_key
        SECRETKEY = credenciales.bingx_api_secret

        # Modificar el apalancamiento
        def apalancamiento():
            payload = {}
            path = '/openApi/swap/v2/trade/leverage'
            method = "POST"
            paramsMap = {
            "leverage": leverage,
            "side": positionSide,
            "symbol": symbol,
            "timestamp": int(time.time()*1000)
        }
            paramsStr = parseParam(paramsMap)
            return send_request(method, path, paramsStr, payload)
        
        # Coloacar la orden
        def demo():
            payload = {}
            path = '/openApi/swap/v2/trade/order'
            method = "POST"
            paramsMap = {
            "symbol": f"{symbol}",
            "side": f"{side}",
            "positionSide": positionSide,
            "type": f"{order_type}",
            "quantity": quantity,
            "price": price
        }
            paramsStr = parseParam(paramsMap)
            return send_request(method, path, paramsStr, payload)

        def get_sign(api_secret, payload):
            signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
            #print("sign=" + signature)
            return signature


        def send_request(method, path, urlpa, payload):
            url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
            #print(url)
            headers = {
                'X-BX-APIKEY': APIKEY,
            }
            response = requests.request(method, url, headers=headers, data=payload)
            return response.text

        def parseParam(paramsMap):
            sortedKeys = sorted(paramsMap)
            paramsStr = "&".join(["%s=%s" % (x, paramsMap[x]) for x in sortedKeys])
            if paramsStr != "": 
                return paramsStr+"&timestamp="+str(int(time.time() * 1000))
            else:
                return paramsStr+"timestamp="+str(int(time.time() * 1000))
        
        print(int(time.time()*1000))
        print(apalancamiento())
        order = json.loads(demo())
        print(f"Orden colocada en {order['data']['order']['price']}. ID:", order['data']['order']['orderId'])
        print("")


    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BINGX")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN DE OKX NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def okx_nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:

        # Definir la posicion segun el lado
        if side == "BUY":
            posSide = "long"
        if side == "SELL":
            posSide = "short"
        
        # Ajustar el apalancamiento
        print("")
        accountAPI.set_leverage(
                                    instId=symbol,
                                    lever=str(leverage),
                                    mgnMode="cross"
                                )
        print("")

        # Colocar la orden
        order = tradeAPI.place_order(
                                        instId=symbol,
                                        tdMode="cross",
                                        side=side.lower(),
                                        posSide=posSide,
                                        ordType=order_type.lower(),
                                        px=str(price),
                                        sz=str(quantity)
                                    )
        print("")
        
        if order["code"] == "0":
            print(f"Orden colocada en {price}. ID:", order["data"][0]["ordId"])
            print("")
        else:
            print("ERROR COLOCANDO LA ORDEN EN OKX, error_code = ",order["data"][0]["sCode"], ", Error_message = ", order["data"][0]["sMsg"])
            print("")
    
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN OKX")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN DE KUCOIN NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def kucoin_nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Definir la cantidad en lotes para poder colocar la orden
        lote = kucoin_futures.client.Market().get_contract_detail(symbol="PEOPLEUSDTM")['multiplier']
        quantity = quantity/lote
        
        # Colocar la orden segun el tipo
        side = side.lower()
        if order_type == "LIMIT":
            order = kucoin_client.create_limit_order(
                                                        symbol=symbol,
                                                        side=side,
                                                        lever=leverage,
                                                        size=quantity,
                                                        price=price,
                                                    )
            
        if order_type == "MARKET":
            order = kucoin_client.create_market_order(
                                                        symbol=symbol,
                                                        side=side,
                                                        lever=leverage,
                                                        size=quantity,
                                                    )
    
        print(f"Orden colocada en {price}. ID:", order["orderId"])
        print("")

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN KUCOIN")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN DE GATEIO NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def gateio_nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Modificar el apalancamiento
        futures_api.update_dual_mode_position_leverage('usdt', symbol, leverage)

        # Definir el lado
        if side == "SELL":
            quantity = -quantity
        
        tif = "gtc"
        if order_type == "MARKET":
            price = 0
            tif = "ioc"

        # Detalles de la orden LIMIT
        order = FuturesOrder(
            contract=symbol,    # Contrato de futuros, por ejemplo, BTC/USDT
            size=quantity,      # Cantidad de contratos a comprar/vender
            price=str(price),   # Precio límite
            tif=tif,            # 'gtc' para limit y 'ioc' para market
            reduce_only=False,  # Indica si es una orden de solo reducción
            is_close=False      # Indica si es una orden de cierre
        )
        
        # Colocar la orden LIMIT
        response = futures_api.create_futures_order('usdt', order)
        #print(response)
        
        print(f"Orden colocada en {response.price}. ID:", response.id)
        print("")
    
    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN GATEIO")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN UNIVERSAL QUE CREA UNA ORDEN LIMITI Ó MARKET
#-----------------------------------------------------
def nueva_orden(exchange, symbol, order_type, quantity, price, side, leverage):
    try:

        exchange = exchange.upper()
        symbol = symbol.upper()
        order_type = order_type.upper()
        side = side.upper()

        # Definir el Símbolo segun el exchange
        symbol = definir_symbol(exchange=exchange, symbol=symbol)
        
        # BINANCE
        if exchange == "BINANCE":
            binance_nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # BYBIT
        if exchange == "BYBIT":
            bybit_nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # BITGET
        if exchange == "BITGET":
            bitget_nueva_orden(symbol, order_type, quantity, price, side, leverage)    

        # BINGX
        if exchange == "BINGX":
            bingx_nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # OKX
        if exchange == "OKX":
            okx_nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # KUCOIN
        if exchange == "KUCOIN":
            kucoin_nueva_orden(symbol, order_type, quantity, price, side, leverage)

        # GATEIO
        if exchange == "GATEIO":
            gateio_nueva_orden(symbol, order_type, quantity, price, side, leverage)

    except Exception as e:
        print("ERROR CREANDO LA ORDEN")
        print(e)
        print("")
#-----------------------------------------------------

#nueva_orden(exchange="bitget", symbol="ordi", order_type="LIMIT", quantity=0.5, price=57.2, side="buy", leverage=9)

