from binance.client import Client
from pybit.unified_trading import HTTP
import time
import pygame
from gtts import gTTS
from datetime import datetime
from colorama import init, Fore
import asyncio
import pandas as pd


client = Client(api_key="", api_secret="", tld="com")
session = HTTP(testnet=False)


# CONFIGURACIÓN DE PARAMETROS
#----------------------------------------------
# ENTRADAS RECOMENDADAS
iniciar = True            # Iniciar búsqueda
print("")
error = 1
while error == 1:
    try:
        exchange = input("Introduce el exchange: ").upper()
        variacion_precio = float(input("Introduce la variación del precio: "))    # Variación en el precio (porcentaje)
        variacion_oi = float(input("Introduce la variación del OI: "))            # Variación en el open interest (porcentaje)
        cantidad_velas = int(input("Introduce la cantidad de velas (5M): "))      # Temporalidad de 5 minuto
        volumen24h = int(input("Introduce el volumen en 24H: "))                  # Volumen en 24 horas
        sr = input("Soportes y Resistencias (SI/NO): ").upper()                     # Depende si la busqueda utiliza soportes y resistencias
        error = 0
    
    except Exception as e:
        print("DATO INCORRECTO!")
        print("")
tiempo_de_espera = 2                                                              # Tiempo de espera para una nueva busqueda
tiempo_recuperacion = 3                                                           # Tiempo de recuperción después de un error
tiempo_de_iteracion = 0.1                                                         # Tiempo de iteracción entre cada tick

# ENTRADAS MANUAL
'''
print("")
print("INGRESE LOS PARAMETROS DE LA BÚSQUEDA")
iniciar = True                                         # Iniciar busqueda True o False
print("")
variacion_precio = int(input("Variación del precio: "))     # Variación en el precio
print("")
variacion_oi = int(input("Variación del OI: "))            # Variación en el open interest
print("")
cantidad_velas = int(input("Cantidad de velas (5M): "))         # Temporalidad de 5 minuto
print("")
volumen24h = int(input("Volumen mínimo en 24H: "))                # Volumen en 24 horas
print("")
tiempo_de_espera = int(input("Tiempo de espera para la siguiente búsquedamacho: "))    # Tiempo de espera para una nueva busqueda
'''
#----------------------------------------------


# FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT
#------------------------------------------------------
def buscar_ticks():
    try:
        i = 0
        ticks =[]
        
        if exchange.upper() == "BINANCE":
            lista_ticks = client.futures_symbol_ticker() #Buscar todos los pares de monedas
        if exchange.upper() == "BYBIT":
            lista_ticks = session.get_tickers(category="linear")['result']['list'] #Buscar todos los pares de monedas

        for tick in lista_ticks:
            i = i + 1
            if "USDT" in str(tick["symbol"]):
                #print(tick["symbol"], i)
                ticks.append(str(tick["symbol"]))
        #print ("Cantidad de Monedas encontradas en par USDT:", len(ticks))
        return ticks
   
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT (buscar_ticks())")
        print(e)
        e = "error"
        print("")
        ticks = []
        return ticks
#-------------------------------------------------------------


# FUNCIÓN QUE BUSCA TODA LA INFO DE UN PAR
#----------------------------------------
def info_tick(tick):
    try:
        info = client.futures_ticker(symbol=tick) #Busca la info de una moneda
        #print (info)
        return info
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE BUSCA TODA LA INFO DE UN PAR. (info_tick())")
        print(e)
        print("")
        info = {}
        return info
#----------------------------------------


# FUNCIÓN QUE OBTIENE EL VOLUMEN DE 24H EN USDT DE UN PAR
#-------------------------------------------------------
def volumen_24h(tick):
    try:
        if exchange.upper() == "BINANCE":
            volumen = float(info_tick(tick)["quoteVolume"])
        if exchange.upper() == "BYBIT":
            volumen = float(session.get_tickers(category="linear", symbol=tick)['result']['list'][0]['turnover24h'])
        #print("VOLUMEN EN 24H:", volumen)
        return volumen
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE OBTIENE EL VOLUMEN DE 24H EN USDT DE UN PAR. (volumen_24h())")
        print(e)
        print("")
        volumen = 0
        return volumen
#--------------------------------------------------------


# FUNCIÓN QUE FORMATEA EN "K", "M", "B" y "T" UN NÚMERO
#---------------------------------------
def formato_abreviado(numero):
    try:

        abreviaciones = ['', 'K', 'M', 'B', 'T']  # Abreviaciones para miles, millones, billones, trillones, etc.
        for i in range(len(abreviaciones)):
            factor = 1000 ** i
            if abs(numero) < 1000 ** (i + 1):
                return '{:.1f}{}'.format(numero / factor, abreviaciones[i])
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE FORMATEA EN 'K', 'M', 'B' y 'T' UN NÚMERO. (formato_abreviado())")
        print(e)
        print("")
        return 0
#----------------------------------------


# FUNCIÓN PARA OBTENER LAS ÚLTIMAS X VELAS DEL PRECIO EN 5 MINUTO DE UN PAR
#---------------------------------------------------------------
def obtener_velas_precio(tick):
    try:
        
        if exchange.upper() == "BINANCE":
            velas = client.futures_klines(symbol=tick, interval=Client.KLINE_INTERVAL_5MINUTE, limit=cantidad_velas)
        
        if exchange.upper() == "BYBIT":
          velas = session.get_kline(category="linear", symbol=tick, interval=5, limit=cantidad_velas)['result']['list']

        velas.sort()
        return velas
    except Exception as e:
        print("ERROR EN LA FUNCIÓN PARA OBTENER LAS ÚLTIMAS X VELAS DEL PRECIO EN 5 MINUTO DE UN PAR. (obtener_velas_precio())")
        print(e)
        print("")
        velas = []
        return velas
#----------------------------------------


# FUNCIÓN PARA OBTENER LAS ÚLTIMAS X VELAS DEL OPEN INTEREST EN 5 MINUTO DE UN PAR
#---------------------------------------------
def obtener_velas_oi(tick):
    try:
        
        if exchange.upper() == "BINANCE":
            oi = client.futures_open_interest_hist(symbol=tick, period = "5m", limit=cantidad_velas) # Busca el open interest de una moneda
        
        if exchange.upper() == "BYBIT":
            oi = session.get_open_interest(category="inverse", symbol="BTCUSD", intervalTime="5min",limit=cantidad_velas)['result']['list']
        
        return oi
    except Exception as e:
        print("ERROR EN LA FUNCIÓN PARA OBTENER LAS ÚLTIMAS X VELAS DEL OPEN INTEREST EN 5 MINUTO DE UN PAR. (obtener_velas_oi())")
        print(e)
        print("")
        oi = []
        return oi
#---------------------------------------------


# FUNCIÓN QUE MIDE EL PORCENTAJE DE DISTANCIA EN EL PRECIO ENTRE LA VELA INICIAL Y FINAL DE UN CONJUNTO DE VELAS
#-------------------------------------------------------------------------------------------------
def porcentaje_precio(tick):
    try:
        velas = obtener_velas_precio(tick)
        if len(velas) >= 2:
            vela_inicial = float(velas[-1][4])
            vela_final = float(velas[0][4])
            porcentaje = round(((vela_final - vela_inicial)/vela_inicial)*100, 2)
            #print("PRECIO VELA INICIAL:", vela_inicial, "PRECIO VELA FIANAL:", vela_final)
            #print(porcentaje)
            return porcentaje
        return 0
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE MIDE EL PORCENTAJE DE DISTANCIA EN EL PRECIO ENTRE LA VELA INICIAL Y FINAL DE UN CONJUNTO DE VELAS. (porcentaje_precio())")
        print(e)
        print("")
        return 0
#----------------------------------------------------------------------------------------------------


# FUNCIÓN QUE MIDE EL PORCENTAJE DE DISTANCIA EN EL OPEN INTEREST ENTRE LA VELA INICIAL Y FINAL DE UN CONJUNTO DE VELAS
#-------------------------------------------------------------------------------------------------
def porcentaje_oi(tick):
    try:
        velas = obtener_velas_oi(tick)
        if len(velas) >= 2:
            
            if exchange.upper() == "BINANCE":
                vela_inicial = float(velas[0]["sumOpenInterest"])
                vela_final = float(velas[-1]["sumOpenInterest"])
            
            if exchange.upper() == "BYBIT":
                vela_inicial = float(velas[0]["openInterest"])
                vela_final = float(velas[-1]["openInterest"])
            
            porcentaje = round(((vela_final - vela_inicial)/vela_inicial)*100, 2)
            #print("OI VELA INICIAL:", vela_inicial, "OI VELA FIANAL:", vela_final)
            #print(porcentaje)
            
            return porcentaje
        return 0
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE MIDE EL PORCENTAJE DE DISTANCIA EN EL OPEN INTEREST ENTRE LA VELA INICIAL Y FINAL DE UN CONJUNTO DE VELAS. (porcentaje_oi())")
        print(e)
        print("")
        return 0
#----------------------------------------------------------------------------------------------------


# FUNCIÓN QUE GENERA UN ARCHIVO DE AUDIO A PARTIR DE UN TEXTO
#------------------------------------------------------------
def texto_audio(texto):
    try:
        # Eliminar la palabra "USDT"
        texto = texto.replace("USDT", "")
        
        # Elegir el idioma
        idioma = "es"
        
        #Escoger el tipo de voz
        voz = "female"
        
        # Indicar el texto, idioma y velocidad de lectura
        tts = gTTS(text=texto, lang=idioma, slow=False)
        
        # Generar el archivo de audio
        tts.save("alerta_voz.mp3")
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE GENERA UN ARCHIVO DE AUDIO A PARTIR DE UN TEXTO. (texto_audio())")
        print(e)
        print("")
        tts = gTTS(text="ERROR", lang=idioma, slow=False)
        tts.save("alerta_voz.mp3")
#------------------------------------------------------------


# FUNCIÓN PARA REPRODUCIR SONIDOS
#--------------------------------
async def reproducir_audio(audio):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE REPRODUCE AUDIO")
        print(e)
# -------------------------------


# FUNCIÓN QUE CALCULA LOS SOPORTES Y LAS RESISTENCIAS
#----------------------------------------------------
def soportes_resistencias(tick, intervalo = Client.KLINE_INTERVAL_4HOUR, cantidad_velas=500):
    # Símbolo del par de criptomonedas que deseas obtener
    symbol = tick

    # Obtiene los datos de precios históricos
    historical_data = client.futures_klines(symbol=symbol, interval=intervalo, limit=cantidad_velas)

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
    
    # SOPORTES
    # Soportes Close
    soportes_close = df[df.close == df.close.rolling(ventana, center=True).min()].close
    soporte_close_list = soportes_close.values.tolist()

    for indice1, valor1 in soportes_close.items():
        for indice2, valor2 in soportes_close.items():
            diferencia = 100*abs(valor1-valor2)/valor1
            if diferencia < porcentaje and diferencia != 0.0:
                if valor1 > valor2:
                    if valor1 in soporte_close_list:
                        soporte_close_list.remove(valor1)
                else:
                    if valor2 in soporte_close_list:
                        soporte_close_list.remove(valor2)
    #print(soporte_close_list)
    
    # Soportes Low
    soportes_low = df[df.low == df.low.rolling(ventana, center=True).min()].low
    soporte_low_list = soportes_low.values.tolist()

    for indice1, valor1 in soportes_low.items():
        for indice2, valor2 in soportes_low.items():
            diferencia = 100*abs(valor1-valor2)/valor1
            if diferencia < porcentaje and diferencia != 0.0:
                if valor1 > valor2:
                    if valor1 in soporte_low_list:
                        soporte_low_list.remove(valor1)
                else:
                    if valor2 in soporte_low_list:
                        soporte_low_list.remove(valor2)
    #print(soporte_low_list)
    
    # RESISTENCIAS
    # Resistencias Close
    resistencias_close = df[df.close == df.close.rolling(ventana, center=True).max()].close
    resistencias_close_list = resistencias_close.values.tolist()

    for indice1, valor1 in resistencias_close.items():
        for indice2, valor2 in resistencias_close.items():
            diferencia = 100*abs(valor1-valor2)/valor1
            if diferencia < porcentaje and diferencia != 0.0:
                if valor1 < valor2:
                    if valor1 in resistencias_close_list:
                        resistencias_close_list.remove(valor1)
                else:
                    if valor2 in resistencias_close_list:
                        resistencias_close_list.remove(valor2)
    #print(resistencias_close_list)
    
    # Resistencia High
    resistencias_high = df[df.high == df.high.rolling(ventana, center=True).max()].high
    resistencias_high_list = resistencias_high.values.tolist()

    for indice1, valor1 in resistencias_high.items():
        for indice2, valor2 in resistencias_high.items():
            diferencia = 100*abs(valor1-valor2)/valor1
            if diferencia < porcentaje and diferencia != 0.0:
                if valor1 < valor2:
                    if valor1 in resistencias_high_list:
                        resistencias_high_list.remove(valor1)
                else:
                    if valor2 in resistencias_high_list:
                        resistencias_high_list.remove(valor2)
    #print(resistencias_high_list)

    # Retornar los soportes y las resistencias
    return (soporte_close_list, soporte_low_list, resistencias_close_list, resistencias_high_list)
#----------------------------------------------------


# FUNCION QUE VERIFICA SI UN SOPRTE O RESISTENCIA ESTA CERCA DEL PRECIO ACTUAL
#-----------------------------------------------------------------------------
async def verificar_SR(tick, tipo):
    try:
        velas = obtener_velas_precio(tick)
        precio_actual = float(velas[-1][4])
        separacion = 0.01
        soportes_close, soportes_low, resistencias_close, resistencias_high = soportes_resistencias(tick)
        
        if tipo.upper() == "SHORT":
            for resistencia in resistencias_close:
                if abs(resistencia-precio_actual)/precio_actual < separacion and resistencia > precio_actual:
                    texto_audio("Posible SHORT en " + str(tick))
                    await reproducir_audio('alerta_voz.mp3')

        if tipo.upper() == "LONG":
            for soporte in soportes_close:
                if abs(soporte-precio_actual)/precio_actual < separacion and soporte < precio_actual:
                    texto_audio("Posible LONG en " + str(tick))
                    await reproducir_audio('alerta_voz.mp3')
    except Exception as e:
        print("ERROR VERIFICANDO SOPORTES Y RESISTENCIAS")
        print(e)
#-----------------------------------------------------------------------------


#FUNCIÓN QUE ENVIA LAS ALERTAS
#------------------------------------------------
async def alertas(tick):
    try:
        #print(tick)
        porcentaje_interes_abierto = porcentaje_oi(tick)
        #print(porcentaje_interes_abierto)
        
        # Gestionar errores del OI
        if porcentaje_interes_abierto == 0:
            return "ERROR"
        
        # SHORT Y LONG
        if porcentaje_interes_abierto > variacion_oi:
            porcentaje_precios = porcentaje_precio(tick)
            #print(porcentaje_precios)
            
            if abs(porcentaje_precios) > variacion_precio:
                volumen = volumen_24h(tick)
                if volumen >= volumen24h:
                    
                    # SHORT
                    if porcentaje_precios < 0:
                        print(Fore.RED + "SHORT" + Fore.RESET + ": ", tick)
                        print("Variación del precio:", str(porcentaje_precios) + "%")
                        print("Variación del OI:", str(porcentaje_interes_abierto) + "%")
                        print("Volumen en 24H:", formato_abreviado(volumen))
                        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                        print("")
                        if sr == "SI":
                            # Verificar las resistencias
                            await verificar_SR(tick,"SHORT")
                        else:
                            texto_audio("Posible SHORT en " + str(tick))
                            await reproducir_audio('alerta_voz.mp3')

                    
                    # LONG
                    if porcentaje_precios > 0:
                        print(Fore.GREEN + "LONG" + Fore.RESET + ": ", tick)
                        print("Variación del precio:", str(porcentaje_precios) + "%")
                        print("Variación del OI:", str(porcentaje_interes_abierto) + "%")
                        print("Volumen en 24H:", formato_abreviado(volumen))
                        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                        print("")
                        if sr == "SI":
                            # Verificar las resistencias
                            await verificar_SR(tick,"LONG")
                        else:
                            texto_audio("Posible LONG en " + str(tick))
                            await reproducir_audio('alerta_voz.mp3')
        
        # DIVERGENCIA Y REVERSION
        if porcentaje_interes_abierto < -variacion_oi:
            porcentaje_precios = porcentaje_precio(tick)
            #print(porcentaje_precios)
            
            if abs(porcentaje_precios) > variacion_precio:
                volumen = volumen_24h(tick)
                if volumen >= volumen24h:
                    
                    # SHORT DIVERGENCIA
                    if porcentaje_precios > 0:
                        print(Fore.RED + "SHORT" + Fore.RESET + ": ", tick)
                        print("Variación del precio:", str(porcentaje_precios) + "%")
                        print("Variación del OI:", str(porcentaje_interes_abierto) + "%")
                        print("Volumen en 24H:", formato_abreviado(volumen))
                        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                        print("")
                        if sr == "SI":
                            # Verificar las resistencias
                            await verificar_SR(tick,"SHORT")
                        else:
                            texto_audio("DIVERGENCIA en " + str(tick))
                            await reproducir_audio('alerta_voz.mp3')
                    
                    # LONG REVERSIÓN
                    if porcentaje_precios < 0:
                        print(Fore.GREEN + "LONG" + Fore.RESET + ": ", tick)
                        print("Variación del precio:", str(porcentaje_precios) + "%")
                        print("Variación del OI:", str(porcentaje_interes_abierto) + "%")
                        print("Volumen en 24H:", formato_abreviado(volumen))
                        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                        print("")
                        if sr == "SI":
                            # Verificar las resistencias
                            await verificar_SR(tick,"LONG")
                        else:
                            texto_audio("REVERSIÓN en " + str(tick))
                            await reproducir_audio('alerta_voz.mp3')

    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE ENVIA LAS ALERTAS. (alertas())")
        print(e)
        print("")
#------------------------------------------------


# PROGRAMA PRINCIPAL
#'''
while iniciar:
        try:
            i = 0
            ii = 0
            print("")
            print("PARÁMETROS DE BÚSQUEDA:")
            print("Exchange:", exchange)
            print("Variación del precio:", str(variacion_precio)+"%")
            print("Variación del OI:", str(variacion_oi)+"%")
            print("Cantidad de velas(5M):", cantidad_velas)
            print("Volumen mínimo en 24H:", formato_abreviado(volumen24h))
            print("Soprtes y Resistencias:", sr)
            print("")
            ticks = buscar_ticks()
            print("Buscando en", len(ticks), "monedas disponibles...")
            print("")
            for tick in ticks:
                i = i + 1
                #print (i, tick)
                alerta =  asyncio.run(alertas(tick))
                '''
                # Gestionando errores
                if alerta == "ERROR":
                    ii = ii + 1
                    if ii >= 3:
                        print("ERROR EN LA BUSQUEDA")
                        print("Esperando tiempo de recuperación,", tiempo_recuperacion, "Segundos...")
                        print("")
                        time.sleep(tiempo_recuperacion)
                        ii = 0
                        print("Buscando...")
                        print("")
                #--------------------
                '''
                time.sleep(tiempo_de_iteracion)
            print("Siguiente búsqueda en", tiempo_de_espera, "Segundos...")
            time.sleep(tiempo_de_espera)
        except Exception as e:
            texto_audio("Error en la búsqueda, esperando " + str(tiempo_recuperacion) + " Segundos...")
            print("ERROR EN LA BUSQUEDA")
            print(e)
            print("Esperando tiempo de recuperación.", tiempo_recuperacion, "Segundos...")
            print("")
            asyncio.run(reproducir_audio('alerta_voz.mp3'))
            time.sleep(tiempo_recuperacion)
#'''