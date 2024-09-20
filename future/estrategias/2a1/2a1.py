import future.future as future
import time


try:
    # PARAMETROS DE LA ESTRATEGIAS
    # ----------------------------
    exchange = ""
    symbol = ""
    side = ""
    order_type = ""
    cantidad = 0
    precio = 0
    apalancamiento = 20
    take_profit = 4
    stop_loss = 2
    # ----------------------------

    # Colocar orden Market
    future.nueva_orden(
                    exchange=exchange, 
                    symbol=symbol, 
                    order_type=order_type, 
                    quantity=cantidad, 
                    price=precio, 
                    side=side, 
                    leverage=apalancamiento
                    )

    # Esperar que abra la posición para colocar Stop Loss y Take Profit
    posiciones = future.obtener_posicion(exchange=exchange, symbol=symbol)
    while posiciones != []:
       pass
    
    # Identificar la posicion
    if side == "BUY":
        positionSide = "LONG"
        sl = precio*(100 - stop_loss)/100
        tp = precio*(100 + take_profit)/100
    if side == "SELL":
        positionSide = "SHORT"
        sl = precio*(100 + stop_loss)/100
        tp = precio*(100 - take_profit)/100

    # Colocar Stop Loss
    future.stop_loss(
                    exchange=exchange,
                    symbol=symbol,
                    positionSide=positionSide,
                    stopPrice=sl
                    )

    # Colocar Take profit
    future.take_profit(
                    exchange=exchange,
                    symbol=symbol,
                    positionSide=positionSide,
                    stopPrice=tp,
                    type="LIMIT"
                    )
except Exception as e:
    print("ERROR EJECUTANDO ESTRATEGIA 2a1 MARKET")
    print(e)
    print("")