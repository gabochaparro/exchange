import credenciales
import pybitget
import json
import time


# Definir el cliente para BitGet
bitget_client = pybitget.Client(
                            api_key=credenciales.bitget_api_key, 
                            api_secret_key=credenciales.bitget_api_secret, 
                            passphrase = credenciales.bitget_api_passphrase, 
                            use_server_time=False,
                        )

# FUNCIÓN DE BITGET NUEVA ORDEN 'LIMIT' O 'MARKET'
# ------------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
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