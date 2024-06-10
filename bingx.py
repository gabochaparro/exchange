import credenciales
import time
import json

# FUNCIÓN DE BINGX NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
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