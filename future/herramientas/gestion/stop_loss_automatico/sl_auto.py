import future
import json
import time

def sl_auto(symbol, tipo, perdida_usdt):
    precio_sl_actual = ""    
    while True:
        try:
            # Ordenes abiertas y posiciones
            ordenes = future.obtener_ordenes("BYBIT",symbol)
            posiciones = future.obtener_posicion("BYBIT",symbol)
            #print(json.dumps(ordenes,indent=2))

            # Precio promedio de la posición y tamaño long
            pos_long_precio = ""
            pos_long_tamaño = ""
            for pos in posiciones:
                if pos['positionIdx'] == 1:
                    pos_long_precio = pos['avgPrice']
                    pos_long_tamaño = pos['size']

            # Precio promedio de la posición y tamaño short
            pos_short_precio = ""
            pos_short_tamaño = ""
            for pos in posiciones:
                if pos['positionIdx'] == 2:
                    pos_short_precio = pos['avgPrice']
                    pos_short_tamaño = pos['size']

            # Precio promedio total
            numerdador_long = float(pos_long_precio)*float(pos_long_tamaño)
            denominador_long = float(pos_long_tamaño)
            numerdador_short = float(pos_short_precio)*float(pos_short_tamaño)
            denominador_short = float(pos_short_tamaño)
            orderId = ""
            for orden in ordenes:
                # SL actual
                if orden['stopOrderType'] == "StopLoss":
                    orderId = orden['orderId']
                    precio_sl_actual = float(orden['triggerPrice'])

                # Long
                if orden['positionIdx'] == 1 and not(orden['reduceOnly']) and orden['orderType'] == "Limit":
                    numerdador_long = numerdador_long + float(orden['price'])*float(orden['qty'])
                    denominador_long = denominador_long + float(orden['qty'])
                # Short
                if orden['positionIdx'] == 2 and not(orden['reduceOnly']) and orden['orderType'] == "Limit":
                    numerdador_short = numerdador_short + float(orden['price'])*float(orden['qty'])
                    denominador_short = denominador_short + float(orden['qty'])

            # Precio promedio total lonng
            if denominador_long != 0:
                precio_promedio_long = numerdador_long/denominador_long
                print(json.dumps(precio_promedio_long,indent=2))

            # Precio promedio total lonng
            if denominador_short != 0:
                precio_promedio_short = numerdador_short/denominador_short
                print(json.dumps(precio_promedio_short,indent=2))

            if tipo == "LONG":
                precio_sl = precio_promedio_long - perdida_usdt/denominador_long
                if precio_sl != precio_sl_actual:
                    future.cancelar_orden(symbol, orderId=orderId)
                    future.stop_loss(symbol=symbol, positionSide="LONG", stopPrice=precio_sl, slSize="")
            if tipo == "SHORT":
                precio_sl = precio_promedio_short + perdida_usdt/denominador_short
                if precio_sl != precio_sl_actual:
                    future.cancelar_orden(symbol, orderId=orderId)
                    future.stop_loss(symbol=symbol, positionSide="SHORT", stopPrice=precio_sl, slSize="")
            time.sleep(3.6)
        except Exception as e:
            print(f"ERROR EN LA FUNCION sl_auto()\n{e}")