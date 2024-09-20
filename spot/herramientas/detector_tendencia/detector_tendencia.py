# FUNCIÓN QUE DETECTA LA TENDENCIA DE UN ACTIVO
# ---------------------------------------------
def detectar_tendencia(exchange, symbol):
    
    from binance.client import Client
    from pybit.unified_trading import HTTP
    import json

    client = Client(api_key="", api_secret="", tld="com")
    session = HTTP(testnet=False)


    # CONFIGURACIÓN DE PARAMETROS
    #----------------------------------------------
    exchange = exchange.upper()
    symbol = symbol.upper()+"USDT"
    cantidad_velas = 3
    intervalos = ["1M","5M","1H","4H","1D","1S"]
    #----------------------------------------------

    # FUNCIÓN PARA OBTENER LAS ÚLTIMAS X VELAS DEL PRECIO DE UN PAR EN DETERMINADO INTERVALO
    #---------------------------------------------------------------------------------------
    def obtener_velas_precio(symbol,interval):
        try:

            symbol = symbol.upper()
            interval = interval.upper()

            # BINANCE
            if exchange.upper() == "BINANCE":
                
                # Definir intervalos
                if interval == "1M":
                    interval = Client.KLINE_INTERVAL_1MINUTE
                if interval == "5M":
                    interval = Client.KLINE_INTERVAL_5MINUTE
                if interval == "30M":
                    interval = Client.KLINE_INTERVAL_30MINUTE
                if interval == "1H":
                    interval = Client.KLINE_INTERVAL_1HOUR
                if interval == "4H":
                    interval = Client.KLINE_INTERVAL_4HOUR
                if interval == "1D":
                    interval = Client.KLINE_INTERVAL_1DAY
                if interval == "1S":
                    interval = Client.KLINE_INTERVAL_1WEEK
                
                # Obtener las velas
                velas = client.get_klines(symbol=symbol, interval=interval, limit=cantidad_velas)
                #print(velas)
            
            # BYBIT
            if exchange.upper() == "BYBIT":
                
                # Definir intervalos
                if interval == "1M":
                    interval = "1"
                if interval == "5M":
                    interval = "5"
                if interval == "30M":
                    interval = "30"
                if interval == "1H":
                    interval = "60"
                if interval == "4H":
                    interval = "240"
                if interval == "1D":
                    interval = "D"
                if interval == "1S":
                    interval = "W"
            
                # Obtener las velas
                velas = session.get_kline(category="spot", symbol=symbol, interval=interval, limit=cantidad_velas)['result']['list']

            velas.sort()
            return velas
        
        except Exception as e:
            print("ERROR EN LA FUNCIÓN. obtener_velas_precio()")
            print(e)
            print("")
            velas = []
            return velas
    #---------------------------------------------------------------------------------------

    # FUNCIÓN QUE DETERMINA LA TENDENCIA SEGÚN LAS VELAS
    # --------------------------------------------------
    def tendencia(symbol,interval):
        try:
            # Incializar variables
            velas = obtener_velas_precio(symbol,interval)
            vela_inicial_apertura = float(velas[0][1])
            vela_medio_apertura = float(velas[1][1])
            vela_medio_cierre = float(velas[1][4])
            vela_final_cierre = float(velas[2][4])
            
            if (vela_medio_cierre > vela_inicial_apertura) and (vela_final_cierre > vela_medio_apertura):
                return "ALCISTA"
            if (vela_medio_cierre < vela_inicial_apertura) and (vela_final_cierre < vela_medio_apertura):
                return "BAJISTA"
            
            return "RANGO"
        
        except Exception as e:
            print("ERROR EN LA FUNCIÓN tendencia()")
            print(e)
            print("")
    # --------------------------------------------------

    # FUNCIÓN QUE DETERMINA LA TENDENCIA TOTAL
    # ----------------------------------------
    def detector():
        try:
            alcistas = 0
            bajistas = 0
            for intervalo in intervalos:
                direccion = tendencia(symbol,intervalo)
                if direccion == "ALCISTA":
                    alcistas = alcistas + 1
                if direccion == "BAJISTA":
                    bajistas = bajistas + 1

            if 3 <= alcistas > bajistas:
                return "ALCISTA", alcistas, "BAJISTA", bajistas
            
            if 3 <= bajistas > alcistas:
                return "BAJISTA", bajistas, "ALCISTA", alcistas
            
            return "RANGO", "ALCISTA", alcistas, "BAJISTA", bajistas

        except Exception as e:
            print("ERROR EN LA FUNCIÓN detector()")
    # ----------------------------------------
    return detector()
# ---------------------------------------------
print(detectar_tendencia("binance","btc"))