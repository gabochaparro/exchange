import credenciales
from okx import Trade, Account, PublicData, MarketData
import json
import time

# Definir la API de OKX
tradeAPI = Trade.TradeAPI(credenciales.okx_api_key, 
                              credenciales.okx_api_secret, 
                              credenciales.okx_api_passphrase, 
                              False, 
                              "0"
                              )
accountAPI = Account.AccountAPI(credenciales.okx_api_key, 
                              credenciales.okx_api_secret, 
                              credenciales.okx_api_passphrase, 
                              False, 
                              "0"
                              )


# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        precio = MarketData.MarketAPI(flag="0").get_ticker(instId=symbol)['data'][0]['last']
        return float(precio)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN OKX")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE OKX NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Definir la cantidad segun el tamaño del lote
        tickes = PublicData.PublicAPI(flag="0").get_instruments(instType="SWAP")['data']
        for tick in tickes:
            if tick['instId'] == symbol:
                lote = float(tick['ctVal'])
                quantity = quantity/lote

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