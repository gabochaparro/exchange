import credenciales     
import time
import requests
import hmac
from hashlib import sha256
import time
import json


# FUNCIÓN QUE LLAMA LA API DE BINGX
# ---------------------------------
def bingx_api(path, method, paramsMap):
    try:
        APIURL = "https://open-api.bingx.com"
        APIKEY = credenciales.bingx_api_key
        SECRETKEY = credenciales.bingx_api_secret

        def demo():
            payload = {}
            
            paramsStr = parseParam(paramsMap)
            return send_request(method, path, paramsStr, payload)

        def get_sign(api_secret, payload):
            signature = hmac.new(api_secret.encode("utf-8"), payload.encode("utf-8"), digestmod=sha256).hexdigest()
            print("sign=" + signature)
            return signature


        def send_request(method, path, urlpa, payload):
            url = "%s%s?%s&signature=%s" % (APIURL, path, urlpa, get_sign(SECRETKEY, urlpa))
            print(url)
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
                 paramsStr+"timestamp="+str(int(time.time() * 1000))

        return json.loads(demo())

    except Exception as e:
        print("ERROR LLAMANDO LA API DE BINGX")
        print(e)
        print("")
# ---------------------------------

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        
        path = '/openApi/swap/v3/quote/klines'
        method = "GET"
        paramsMap = {
            "symbol": str(symbol),
            "interval": "1h",
            "limit": "1"
        }
        result = bingx_api(path=path, method=method, paramsMap=paramsMap)

        precio = float(result['data'][0]['close'])
        return precio
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN BINGX")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE BINGX NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:

        if side == "BUY":
            positionSide = "LONG"
        if side == "SELL":
            positionSide = "SHORT"

        # Modificar el apalancamiento
        path = '/openApi/swap/v2/trade/leverage'
        method = "POST"
        paramsMap = {
                    "leverage": leverage,
                    "side": positionSide,
                    "symbol": symbol,
                    "timestamp": int(time.time()*1000)
                    }
        bingx_api(path=path, method=method, paramsMap=paramsMap)

        # Coloacar la orden
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
        
        order = bingx_api(path=path, method=method, paramsMap=paramsMap)
        if order['code'] == 0:
            print(f"Orden colocada en {order['data']['order']['price']}. ID:", order['data']['order']['orderId'])
        else:
            print("ERROR COLOCANDO LA ORDEN EN BINGX")
            print(order)
        print("")


    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BINGX")
        print(e)
        print("")
# ------------------------------------------------