import json

# FUNCIÓN QUE CALCULA LOS SOPORTES Y LAS RESISTENCIAS EN BINANCE
#---------------------------------------------------------------
def sr_binance(symbol, intervalo="1d", cantidad_velas=360):
    try:
        from binance.client import Client
        import pandas as pd

        client = Client(api_key="", api_secret="", tld="com")
        symbol = symbol.upper()
        sr = []

        # Definir el intervalo
        if intervalo.upper() == "1M":
                intervalo = Client.KLINE_INTERVAL_1MINUTE
        if intervalo.upper() == "5M":
                intervalo = Client.KLINE_INTERVAL_5MINUTE
        if intervalo.upper() == "15M":
                intervalo = Client.KLINE_INTERVAL_15MINUTE
        if intervalo.upper() == "30M":
                intervalo = Client.KLINE_INTERVAL_30MINUTE
        if intervalo.upper() == "1H":
                intervalo = Client.KLINE_INTERVAL_1HOUR
        if intervalo.upper() == "4H":
                intervalo = Client.KLINE_INTERVAL_4HOUR
        if intervalo.upper() == "1D":
                intervalo = Client.KLINE_INTERVAL_1DAY
        if intervalo.upper() == "1W":
                intervalo = Client.KLINE_INTERVAL_1WEEK
        if intervalo.upper() == "M":
                intervalo = Client.KLINE_INTERVAL_1MONTH

        # Obtiene los datos de precios históricos
        historical_data = client.futures_klines(symbol=symbol, interval=intervalo, limit=cantidad_velas)

        # Formatea los datos en un DataFrame de Pandas
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        df = pd.DataFrame(historical_data, columns=columns)
        #print(df)

        # Convertir columnas a los tipos de datos deseados
        df['timestamp'] = pd.to_datetime(df['timestamp']*1000000)
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        #print(df)
        
        aperturas = df['open']
        cierres = df['close']
        tiempos = df['timestamp']
        for i in range(len(cierres)-4):
            
            # Buscar soportes
            soporte = cierres[i+1]
            precio_actual = cierres[len(cierres)-1]
            if precio_actual > soporte and (aperturas[i] < soporte and cierres[i] < soporte > cierres[i+2] and cierres[i+3] < soporte):
                sr.append({
                    "tipo": "SOPORTE", 
                    "temporalidad": intervalo, 
                    "tiempo": str(tiempos[i+1]),
                    "precio": soporte
                    })
            
            # Buscar resistencias
            resistencia = cierres[i+1]
            precio_actual = cierres[len(cierres)-1]
            if precio_actual < resistencia and (aperturas[i] > resistencia and cierres[i] > resistencia < cierres[i+2] and cierres[i+3] > resistencia):
                sr.append({
                    "tipo": "RESISTENCIA", 
                    "temporalidad": intervalo, 
                    "tiempo": str(tiempos[i+1]),
                    "precio": resistencia
                    })
        
        # Retornar los soportes y las resistencias
        return sr

    except Exception as e:
        print(f"\nERROR EN LA FUNCION: sr_binance()\n{e}")
#---------------------------------------------------------------

# FUNCIÓN QUE CALCULA LOS SOPORTES Y LAS RESISTENCIAS EN BYBIT
#---------------------------------------------------------------
def sr_bybit(symbol, intervalo="1d", cantidad_velas=360):
    try:
        from pybit.unified_trading import HTTP
        import pandas as pd
        
        bybit_session = HTTP(testnet=False, api_key="", api_secret="")
        symbol = symbol.upper()
        sr = []

        # Definir el intervalo
        if intervalo.upper() == "1":
                intervalo = "1"
        if intervalo.upper() == "5":
                intervalo = "5"
        if intervalo.upper() == "15":
                intervalo = "15"
        if intervalo.upper() == "30":
                intervalo = "30"
        if intervalo.upper() == "60":
                intervalo = "60"
        if intervalo.upper() == "240":
                intervalo = "240"
        if intervalo.upper() == "D":
                intervalo = "D"
        if intervalo.upper() == "W":
                intervalo = "W"
        if intervalo.upper() == "M":
                intervalo = "M"

        # Obtiene los datos de precios históricos
        historical_data = bybit_session.get_kline(category="linear", symbol=symbol, interval=intervalo, limit=cantidad_velas)['result']['list']
        #print(historical_data)

        # Formatea los datos en un DataFrame de Pandas
        columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        df = pd.DataFrame(historical_data, columns=columns).sort_index(ascending=False).reset_index(drop=True)
        #print(df)

        # Convertir columnas a los tipos de datos deseados
        df['timestamp'] = pd.to_datetime(pd.to_numeric(df['timestamp'])*1000000)
        df['open'] = pd.to_numeric(df['open'])
        df['high'] = pd.to_numeric(df['high'])
        df['low'] = pd.to_numeric(df['low'])
        df['close'] = pd.to_numeric(df['close'])
        #print(df)
        
        aperturas = df['open']
        cierres = df['close']
        tiempos = df['timestamp']
        for i in range(len(cierres)-4):
            
            # Buscar soportes
            soporte = cierres[i+1]
            precio_actual = cierres[len(cierres)-1]
            if precio_actual > soporte and (aperturas[i] < soporte and cierres[i] < soporte > cierres[i+2] and cierres[i+3] < soporte):
                sr.append({
                    "tipo": "SOPORTE", 
                    "temporalidad": intervalo, 
                    "tiempo": str(tiempos[i+1]),
                    "precio": soporte
                    })
            
            # Buscar resistencias
            resistencia = cierres[i+1]
            precio_actual = cierres[len(cierres)-1]
            if precio_actual < resistencia and (aperturas[i] > resistencia and cierres[i] > resistencia < cierres[i+2] and cierres[i+3] > resistencia):
                sr.append({
                    "tipo": "RESISTENCIA", 
                    "temporalidad": intervalo, 
                    "tiempo": str(tiempos[i+1]),
                    "precio": resistencia
                    })
        
        # Retornar los soportes y las resistencias
        return sr
    
    except Exception as e:
        print(f"\nERROR EN LA FUNCION: sr_bybit()\n{e}")
#---------------------------------------------------------------

sr_1m = sr_bybit("WLFIUSDT", "1")
sr_5m = sr_bybit("WLFIUSDT", "5")
sr_15m = sr_bybit("WLFIUSDT", "15")
sr_1h = sr_bybit("WLFIUSDT", "60")
sr_4h = sr_bybit("WLFIUSDT", "240")
sr_d = sr_bybit("WLFIUSDT", "D")
sr_w = sr_bybit("WLFIUSDT", "W")
sr_m = sr_bybit("WLFIUSDT", "M")

sr = sr_1m + sr_5m + sr_15m + sr_1h + sr_4h + sr_d + sr_w + sr_m
print(json.dumps(sr, indent=2))