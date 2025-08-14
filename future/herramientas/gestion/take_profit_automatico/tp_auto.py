import future
import time

def tp_auto(symbol, tipo, distancia_porcentual):
    precio_tp_actual = ""    
    while True:
        try:
            # Ordenes y posicion
            ordenes = future.obtener_ordenes("BYBIT",symbol)
            precio_pos = float(future.obtener_posicion("BYBIT",symbol)[0]['avgPrice'])

            # Buscar el TP actual
            orderId = ""
            for orden in ordenes:
                if orden['stopOrderType'] == "TakeProfit":
                    orderId = orden['orderId']
                    precio_tp_actual = float(orden['triggerPrice'])

            # Colocar el nuevo TP
            if tipo == "LONG":
                precio_tp = precio_pos*(1 + distancia_porcentual/100)
                if precio_tp != precio_tp_actual:
                    future.cancelar_orden(symbol, orderId=orderId)
                    future.take_profit(symbol=symbol, positionSide="LONG", stopPrice=precio_tp, slSize="")
            if tipo == "SHORT":
                precio_tp_actual = precio_pos*(1 - distancia_porcentual/100)
                if precio_tp != precio_tp_actual:
                    future.cancelar_orden(symbol, orderId=orderId)
                    future.take_profit(symbol=symbol, positionSide="SHORT", stopPrice=precio_tp, slSize="")

            time.sleep(3.6)

        except Exception as e:
            print(f"ERROR EN LA FUNCION tp_auto()\n{e}")