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

# FUNCIÓN QUE BUSCA EL APALANCAMIENTO MÁXMIMO DE UN TICK
# ------------------------------------------------------
def apalancameinto_max(symbol):
    try:

        # Modificar el apalancamiento
        path = '/openApi/swap/v2/trade/leverage'
        method = "GET"
        paramsMap = {
                    "symbol": symbol,
                    "timestamp": int(time.time()*1000)
                    }

        # Obtener el apalancamiento máximo
        max_leverage = bingx_api(path, method, paramsMap)['data']['maxLongLeverage']
        return int(max_leverage)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL APALANCAMIENTO MÁXIMO DE {symbol} EN BINGX")
        print(e)
        print("")
# ------------------------------------------------------

# FUNCIÓN DE BINGX NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:

        # Definir el lado
        if side == "BUY":
            positionSide = "LONG"
        if side == "SELL":
            positionSide = "SHORT"

        # Modificar el apalancamiento
        max_leverage = apalancameinto_max(symbol)
        if leverage > max_leverage:
            leverage = max_leverage
        
        path = '/openApi/swap/v2/trade/leverage'
        method = "POST"
        paramsMap = {
                    "leverage": leverage,
                    "side": positionSide,
                    "symbol": symbol,
                    "timestamp": int(time.time()*1000)
                    }
        
        apalancamiento = bingx_api(path=path, method=method, paramsMap=paramsMap)
        if apalancamiento['code'] != 0:
            print("ERROR MODIFICANDO EL APALANCAMIENTO")
            print(apalancamiento)
            print("")

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

        return {
                "orderId": order['data']['order']['orderId'],
                "price": order['data']['order']['price']
                }

    except Exception as e:
        print("ERROR COLOCANDO LA ORDEN EN BINGX")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN QUE CANCELA TODAS LAS ORDENES ABIERTAS
# ----------------------------------------------
def cancelar_ordenes(symbol):
    try:
        
        print("Cancelando ordenes...")
        path = '/openApi/swap/v2/trade/allOpenOrders'
        method = "DELETE"
        paramsMap = {
                    "symbol": symbol,
                    "recvWindow": 0,
                    "timestamp": str(int(time.time()*1000)),
                    }
        
        ordenes = bingx_api(path=path, method=method, paramsMap=paramsMap)
        
        if ordenes['code'] == 0:
            if  ordenes['msg'] == "" and ordenes['data']['success'] != None:
                print("Se cancelaron todas las ordenes")
                print(ordenes)
                print("")
            else:
                print("NO HAY ORDENES QUE CANCELAR")
        else:
            print("ERROR CANCELANDO TODAS LAS ORDENES DE BINGX")
            print(ordenes)
            print("")

    except Exception as e:
        print("ERROR CANCELANDO TODAS LAS ORDENES DE BINGX")
        print(e)
        print("")
# ----------------------------------------------

# FUNCIÓN PARA OBTENER LA INFO DE LAS ORDENES ABIERTAS
# ----------------------------------------------------
def obtener_ordenes(symbol):
    try:

        # Definir parametros
        path = '/openApi/swap/v2/trade/openOrders'
        method = "GET"
        paramsMap = {
                    "symbol": symbol,
                    "recvWindow": 0,
                    "timestamp": str(int(time.time()*1000)),
                    }
        
        # Obtener las ordenes
        print("Buscando ordenes...")
        oredenes_abiertas = bingx_api(path=path, method=method, paramsMap=paramsMap)
        if oredenes_abiertas['code'] == 0:
            oredenes_abiertas = oredenes_abiertas['data']['orders']
            print(f"{len(oredenes_abiertas)} ordenes encontradas")
            return oredenes_abiertas
        else:
            print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BINGX")
            print(oredenes_abiertas)
            print("")

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS ORDENES ABIERTAS EN BINGX")
        print(e)
        print("")
# ----------------------------------------------------

# FUNCIÓN QUE CANCELA UNA ORDEN
# -----------------------------
def cancelar_orden(symbol, orderId):
    try:

        # Definir parametros
        path = '/openApi/swap/v2/trade/order'
        method = "DELETE"
        paramsMap = {
                    "symbol": symbol,
                    "orderId": orderId,
                    "recvWindow": 0,
                    "timestamp": str(int(time.time()*1000)),
                    }
        
        # Cancelar la orden
        print(f"Eliminando orden {orderId}...")
        orden = bingx_api(path=path, method=method, paramsMap=paramsMap)
        if orden['code'] == 0:
            print(f"Eliminada la orden {orderId} de {symbol}.")
            print("")
        else:
            print(f"ERROR CANCELANDO LA ORDEN {orderId} DE BINGX")
            print(orden)
            print("")
    
    except Exception as e:
        print(f"ERROR CANCELANDO LA ORDEN {orderId} DE BINGX")
        print(e)
        print("")
# -----------------------------

# FUNCIÓN QUE OBTIENE LA INFO DE LAS POSICIONES (No disponible por el momento)
# ---------------------------------------------
def obtener_posicion(symbol):
    try:

        # Definir parametros
        path = ''
        method = "GET"
        paramsMap = {
                    "symbol": symbol,
                    "recvWindow": 0,
                    "timestamp": str(int(time.time()*1000)),
                    }

        return "ESTA FUNCION NO ESTA DISPONIBLE POR EL MOMENTO"

    except Exception as e:
        print("ERROR OBTENIENDO INFO DE LAS POSICIONES DE BYBIT")
        print(e)
        print("")
# ---------------------------------------------

# FUNCIÓN QUE CIERRA UNA POSICION
# -------------------------------
def cerrar_posicion(symbol, positionSide):
    try:

        # Definir lado
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "SELL"
        if positionSide == "SHORT":
            side = "BUY"

        # Definir parametros
        path = ''
        method = "GET"
        paramsMap = {
                    "symbol": symbol,
                    "type": "STOP_MARKET",
                    "side": side,
                    "positionSide": positionSide,
                    "closePosition": "True",
                    "recvWindow": 0,
                    "timestamp": str(int(time.time()*1000)),
                    }
        
        # Cerrar posición
        print("Cerrando posición...")
        print(json.dumps(bingx_api(path=path, method=method, paramsMap=paramsMap)),indent=2)
        
        print(f"Posición {positionSide} Cerrada")
        print("")

    except Exception as e:
        print("ERROR CERRANDO POSICION EN BYBIT")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN STOP LOSS
# -------------------------------
def stop_loss(symbol, positionSide, stopPrice):
    try:

        # Definir lado
        if positionSide == "LONG":
            side = "SELL"
        if positionSide == "SHORT":
            side = "BUY"

        # Definir parametros# Definir parametros
        path = '/openApi/swap/v2/trade/order'
        method = "POST"
        paramsMap = {
                    "symbol": symbol,
                    "type": "STOP_MARKET",
                    "stopLoss": "True",
                    "side": side,
                    "positionSide": positionSide,
                    "closePosition": "True",
                    "stopPrice": stopPrice,
                    "recvWindow": 0,
                    "timestamp": str(int(time.time()*1000)),
                    }
        
        # Colocar la orden de Stop Loss
        orden = bingx_api(path=path, method=method, paramsMap=paramsMap)
        
        print(f"Stop Loss Colocado en {orden}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN BINGX")
        print(e)
        print("")
# -------------------------------

# FUNCIÓN QUE COLOCA UN TAKE PROFIT LIMIT O MARKET
# ------------------------------------------------
def take_profit(symbol, positionSide, stopPrice, type):
    try:

        # Definir lado
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "SELL"
        if positionSide == "SHORT":
            side = "BUY"

        # Definir parametros# Definir parametros
        path = '/openApi/swap/v2/trade/order'
        method = "POST"
        paramsMap = {
                    "symbol": symbol,
                    "type": type.upper(),
                    "side": side,
                    "positionSide": positionSide,
                    "closePosition": "True",
                    "takeProfit": "True",
                    "stopPrice": stopPrice,
                    "recvWindow": 0,
                    "timestamp": str(int(time.time()*1000)),
                    }
        
        # Colocar la orden de Take Profit
        orden = bingx_api(path=path, method=method, paramsMap=paramsMap)

        print(f"Take Profit Colocado en {orden}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO TAKE PROFIT EN BINGX")
        print(e)
        print("")
# ------------------------------------------------

# FUNCIÓN QUE COLOCA UN TRAILING STOP
# -----------------------------------
def trailing_stop(symbol, positionSide, activationPrice, callbackRate):
    try:

        # Definir lado
        positionSide = positionSide.upper()
        if positionSide == "LONG":
            side = "SELL"
        if positionSide == "SHORT":
            side = "BUY"

        # Definir el callbackRate
        callbackRate = callbackRate/100
        
        # Definir parametros# Definir parametros
        path = '/openApi/swap/v2/trade/order'
        method = "POST"
        paramsMap = {
                    "symbol": symbol,
                    "type": "TRAILING_STOP_MARKET",
                    "side": side,
                    "positionSide": positionSide,
                    "closePosition": "True",
                    "activationPrice": activationPrice,
                    "priceRate": callbackRate,
                    "recvWindow": 0,
                    "timestamp": str(int(time.time()*1000)),
                    }
        
        # Colocar la orden del Trailing Stop
        orden = bingx_api(path=path, method=method, paramsMap=paramsMap)
        
        print(f"Trailing Stop Colocado en {orden}.")
        print("")
        return orden
    
    except Exception as e:
        print("ERROR COLOCANDO STOP LOSS EN BYBIT")
        print(e)
        print("")
# -----------------------------------