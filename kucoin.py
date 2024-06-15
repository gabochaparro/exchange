import credenciales
from kucoin_futures.client import Trade, Market
import json
import time


# Definir la API de KuCoin
kucoin_trade_client = Trade(
                            key=credenciales.kucoin_api_key, 
                            secret=credenciales.kucoin_api_secret, 
                            passphrase=credenciales.kucoin_api_passphrase
                            )

# FUNCION QUE BUSCA EL PRECIO ACTUAL DE UN TICK
#--------------------------------------------------------
def precio_actual_activo(symbol):
    try:
        precio = Market().get_contract_detail(symbol=symbol)['markPrice']
        return float(precio)
    
    except Exception as e:
        print(f"ERROR BUSCANDO EL PRECIO ACTUAL DE {symbol} EN KUCOIN")
        print(e)
        print("")
        return 0
#--------------------------------------------------------

# FUNCIÓN DE KUCOIN NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
    try:
        
        # Definir la cantidad en lotes para poder colocar la orden
        lote = Market().get_contract_detail(symbol=symbol)['multiplier']
        quantity = quantity/lote
        
        # Colocar la orden segun el tipo
        side = side.lower()
        if order_type == "LIMIT":
            order = kucoin_trade_client.create_limit_order(
                                                        symbol=symbol,
                                                        side=side,
                                                        lever=leverage,
                                                        size=quantity,
                                                        price=price,
                                                    )
            
        if order_type == "MARKET":
            order = kucoin_trade_client.create_market_order(
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