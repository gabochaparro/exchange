import credenciales
import kucoin_futures.client
import json
import time


# Definir la API de KuCoin
kucoin_client = kucoin_futures.client.Trade(
                                            key=credenciales.kucoin_api_key, 
                                            secret=credenciales.kucoin_api_secret, 
                                            passphrase=credenciales.kucoin_api_passphrase
                                            )


# FUNCIÓN DE KUCOIN NUEVA ORDEN 'LIMIT' O 'MARKET'
# ---------------------------------------------
def nueva_orden(symbol, order_type, quantity, price, side, leverage):
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