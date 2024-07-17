from binance.client import Client
import pandas as pd
import json
import future

client = Client(api_key="", api_secret="", tld="com")

# FUNCIÓN QUE CALCULA LOS SOPORTES Y LAS RESISTENCIAS
#----------------------------------------------------
def soportes_resistencias(exchange, symbol, temporalidad="4H", cantidad_velas="", tipo="close"):
    
    # Símbolo del par de criptomonedas que deseas obtener
    symbol = future.definir_symbol(exchange=exchange, symbol=symbol)

    # Definir la temporalidad
    if temporalidad.upper() == "1M":
        temporalidad = Client.KLINE_INTERVAL_1MINUTE
    if temporalidad.upper() == "5M":
        temporalidad = Client.KLINE_INTERVAL_5MINUTE
    if temporalidad.upper() == "15M":
        temporalidad = Client.KLINE_INTERVAL_15MINUTE
    if temporalidad.upper() == "30M":
        temporalidad = Client.KLINE_INTERVAL_30MINUTE
    if temporalidad.upper() == "1H":
        temporalidad = Client.KLINE_INTERVAL_1HOUR
    if temporalidad.upper() == "4H":
        temporalidad = Client.KLINE_INTERVAL_4HOUR
    if temporalidad.upper() == "1D":
        temporalidad = Client.KLINE_INTERVAL_1DAY
    if temporalidad.upper() == "1W":
        temporalidad = Client.KLINE_INTERVAL_1WEEK
    if temporalidad.upper() == "M":
        temporalidad = Client.KLINE_INTERVAL_1MONTH

    # Obtiene los datos de precios históricos
    historical_data = client.futures_klines(symbol=symbol, interval=temporalidad, limit=cantidad_velas)

    # Formatea los datos en un DataFrame de Pandas
    columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df = pd.DataFrame(historical_data, columns=columns)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    #print(df)

    # Convertir columnas a tipos de datos numéricos
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    #print(df)

    # Porcentaje de separación
    porcentaje = 1
    
    # Ventana de velas
    ventana = 9
    
    # RESISTENCIAS
    # Resistencias Close
    if tipo.lower() == "close":
        resistencias_close = df[df.close == df.close.rolling(ventana, center=True).min()].close
        resistencias = resistencias_close.values.tolist()

        for indice1, valor1 in resistencias_close.items():
            for indice2, valor2 in resistencias_close.items():
                diferencia = 100*abs(valor1-valor2)/valor1
                if diferencia < porcentaje and diferencia != 0.0:
                    if valor1 > valor2:
                        if valor1 in resistencias:
                            resistencias.remove(valor1)
                    else:
                        if valor2 in resistencias:
                            resistencias.remove(valor2)
        #print(resistencias)
    
    # Resistencias Low
    else:
        resistencias_low = df[df.low == df.low.rolling(ventana, center=True).min()].low
        resistencias = resistencias_low.values.tolist()

        for indice1, valor1 in resistencias_low.items():
            for indice2, valor2 in resistencias_low.items():
                diferencia = 100*abs(valor1-valor2)/valor1
                if diferencia < porcentaje and diferencia != 0.0:
                    if valor1 > valor2:
                        if valor1 in resistencias:
                            resistencias.remove(valor1)
                    else:
                        if valor2 in resistencias:
                            resistencias.remove(valor2)
        #print(resistencias)
    
    # SOPORTES
    # Soportes Close
    if tipo.lower() == "close":
        soportes_close = df[df.close == df.close.rolling(ventana, center=True).max()].close
        soportes = soportes_close.values.tolist()

        for indice1, valor1 in soportes_close.items():
            for indice2, valor2 in soportes_close.items():
                diferencia = 100*abs(valor1-valor2)/valor1
                if diferencia < porcentaje and diferencia != 0.0:
                    if valor1 < valor2:
                        if valor1 in soportes:
                            soportes.remove(valor1)
                    else:
                        if valor2 in soportes:
                            soportes.remove(valor2)
        #print(soportes)
    
    # Soporte High
    else:
        soportes_high = df[df.high == df.high.rolling(ventana, center=True).max()].high
        soportes = soportes_high.values.tolist()

        for indice1, valor1 in soportes_high.items():
            for indice2, valor2 in soportes_high.items():
                diferencia = 100*abs(valor1-valor2)/valor1
                if diferencia < porcentaje and diferencia != 0.0:
                    if valor1 < valor2:
                        if valor1 in soportes:
                            soportes.remove(valor1)
                    else:
                        if valor2 in soportes:
                            soportes.remove(valor2)
        #print(soportes)

    # Retornar los soportes y las resistencias
    return (soportes, resistencias, df)
#----------------------------------------------------
