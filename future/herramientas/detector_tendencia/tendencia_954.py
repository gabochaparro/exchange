from binance.client import Client
from pybit.unified_trading import HTTP
import time
import pygame
from gtts import gTTS
from mutagen.mp3 import MP3
from datetime import datetime
from colorama import init, Fore
from collections import Counter
import json
import pandas as pd
import numpy as np


client = Client(api_key="", api_secret="", tld="com")
session = HTTP(testnet=False)


# CONFIGURACIÓN DE PARAMETROS
#----------------------------------------------
# ENTRADAS RECOMENDADAS
iniciar = True            # Iniciar búsqueda
dato_correcto = False
while not dato_correcto:
    try:
        exchange = "BINANCE" #input("Introduce el exchange: ").upper()
        variacion_precio = 1 #float(input("Introduce la variación del precio: "))    # Variación en el precio (porcentaje)
        volumen24h = 100*1000000 #int(input("Introduce el volumen en 24H (M): "))          # Volumen en 24 horas
        coinalyzecom = True
        dato_correcto = True
    
    except Exception as e:
        print("DATO INCORRECTO!")
        print("")
tiempo_de_espera = 2                                # Tiempo de espera para una nueva busqueda
tiempo_recuperacion = 3                             # Tiempo de recuperción después de un error
tiempo_de_iteracion = 1                             # Tiempo de iteracción entre cada tick
temporalidad = Client.KLINE_INTERVAL_1MINUTE        # Temporalidad
cantidad_velas = 13                                 # Cantidad de velas a considerar                                 
#----------------------------------------------


# FUNCIÓN QUE ENCUENTRA TODAS LAS MONEDAS EN EL PAR USDT DE FUTUROS
#------------------------------------------------------------------
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

# FUNCIÓN PARA OBTENER LAS ÚLTIMAS X VELAS DEL
#---------------------------------------------
def obtener_velas_precio(tick,temporalidad, cantidad_velas):
    try:
        
        if exchange.upper() == "BINANCE":
            velas = client.futures_klines(symbol=tick, interval=temporalidad, limit=cantidad_velas)
        
        if exchange.upper() == "BYBIT":
            velas = session.get_kline(category="linear", symbol=tick, interval=1, limit=cantidad_velas)['result']['list']

        velas.sort()
        return velas
    except Exception as e:
        print("ERROR EN LA FUNCIÓN PARA OBTENER LAS ÚLTIMAS X VELAS DEL PRECIO EN 1 MINUTO DE UN PAR. (obtener_velas_precio())")
        print(e)
        print("")
        velas = []
        return velas
#----------------------------------------


# FUNCIÓN QUE MIDE EL PORCENTAJE DE DISTANCIA EN EL PRECIO ENTRE LA VELA INICIAL Y FINAL DE UN CONJUNTO DE VELAS
#-------------------------------------------------------------------------------------------------
def porcentaje_precio(tick, temporalidad, cantidad_velas):
    try:
        velas = obtener_velas_precio(tick, temporalidad, cantidad_velas)
        if len(velas) >= 2:
            vela_final = float(velas[-1][4])
            vela_inicial = float(velas[0][4])
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


# FUNCIÓN QUE GENERA UN ARCHIVO DE AUDIO A PARTIR DE UN TEXTO
#------------------------------------------------------------
def texto_audio(texto):
    try:
        # Variables globales
        global duracion
        # Eliminar la palabra "USDT"
        texto = texto.replace("USDT", "")
        
        # Elegir el idioma
        idioma = "es"
        
        # Indicar el texto, idioma y velocidad de lectura
        tts = gTTS(text=texto, lang=idioma)
        
        # Generar el archivo de audio
        tts.save("alerta_voz.mp3")
                
        # Duracion del audio
        duracion = MP3("alerta_voz.mp3").info.length
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE GENERA UN ARCHIVO DE AUDIO A PARTIR DE UN TEXTO. (texto_audio())")
        print(e)
        print("")
        tts = gTTS(text="ERROR", lang=idioma, slow=False)
        tts.save("alerta_voz.mp3")
#------------------------------------------------------------


# FUNCIÓN PARA REPRODUCIR SONIDOS
#--------------------------------
def reproducir_audio(audio):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play()
        time.sleep(duracion)
        pygame.mixer.music.unload()  # Liberar el archivo después de reproducir
        pygame.mixer.quit()  # Finalizar el mixer
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE REPRODUCE AUDIO")
        print(e)
# -------------------------------

# FUNCIÓN QUE BUSCA MONEDAS EN COINALYZE
# --------------------------------------
def coinalyze():
    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as p:
            # Inicia navegador (abre Chrome/Chromium)
            navegador = p.firefox.launch(headless=True)  # headless=False para ver lo que hace
            pagina = navegador.new_page()

            for i in range(2):
                if i == 0:
                    tipo = "desc"
                if i == 1:
                    tipo = "asc"
                # Abre tu página
                pagina.goto(f"https://es.coinalyze.net/?order_by=oi_24h_pchange&order_dir={tipo}", wait_until="load")

                # Imprimir texto
                texto = pagina.locator("div.table-wrapper").locator("tbody").inner_text()
                #print(texto)
                
                # Organizar los datos
                datos = []
                for linea in texto.splitlines():
                    if linea != "":
                        linea_lista = []
                        for dato in linea.split('\t'):
                            if dato != "":
                                linea_lista.append(dato)
                        datos.append(linea_lista)
                #print(datos)

                # Definir las columnas
                cols = [
                "MONEDA", "PRECIO", "CHG 24H", "MKT CAP", "VOL 24H", "OPEN INTEREST",
                "OI CHG 24H", "OI SHARE", "OI/VOL24H", "FR AVG", "PFR AVG", "LIQS. 24H"
                ]
                        
                # Crear DataFrame
                df = pd.DataFrame(datos, columns=cols)
                if i == 0:
                    df_desc = df
                if i == 1:
                    df_asc = df
            
            # Cerrar el navegador
            #navegador.close()
            
            # Buscar monedas
            df_oi_desc = df_desc[((df_desc["OPEN INTEREST"].str.contains("m")) | (df_desc["OPEN INTEREST"].str.contains("b"))) &
                            ((df_desc["OPEN INTEREST"].str.extract(r"\$([\d\.]+)m").astype(float)[0] > 10) | (df_desc["OPEN INTEREST"].str.contains("b"))) &
                            ((df_desc["VOL 24H"].str.extract(r"\$([\d\.]+)m").astype(float)[0] > 100) | (df_desc["VOL 24H"].str.contains("b")))]
            df_oi_asc = df_asc[((df_asc["OPEN INTEREST"].str.contains("m")) | (df_asc["OPEN INTEREST"].str.contains("b"))) &
                            ((df_asc["OPEN INTEREST"].str.extract(r"\$([\d\.]+)m").astype(float)[0] > 10) | (df_asc["OPEN INTEREST"].str.contains("b"))) &
                            ((df_asc["VOL 24H"].str.extract(r"\$([\d\.]+)m").astype(float)[0] > 100) | (df_asc["VOL 24H"].str.contains("b")))]

            return(df_oi_desc,df_oi_asc)
        
    except Exception as e:
        print(f"\nERROR EN LA FUNCION coinalyze()\n{e}")
# --------------------------------------

# FUNCIÓN QUE BUSCA UNA TENDENCIA 954 EN UN SYMBOL
# ------------------------------------------------
def tendencia_954(exchange, symbol, temporalidad, cantidad_velas, periodo = 9, unbral=80):
    try:
        # Obtener las velas
        if exchange.upper() == "BYBIT":
            velas = session.get_kline(category="linear", symbol=symbol, interval=temporalidad, limit=cantidad_velas)['result']['list']
            velas.sort()
        if exchange.upper() == "BINANCE":
            velas = client.futures_klines(symbol=symbol, interval=temporalidad, limit=cantidad_velas)
            velas.sort()
        
        # Definir las columnas
        if exchange.upper() == "BYBIT":
            columnas = ["startTime", "openPrice", "highPrice", "lowPrice", "closePrice", "volume", "turnover"]
        if exchange.upper() == "BINANCE":
            columnas = ["startTime", "openPrice", "highPrice", "lowPrice", "closePrice", "", "", "", "", "", "", ""]
        
        # Crear el DataFrame
        df = pd.DataFrame(velas, columns=columnas)
        
        # Calcular las Emas
        df["ema"] = df["closePrice"].astype(float).ewm(span=periodo, adjust=False).mean()

        # Poner NaN en las primeras N-1 filas
        df.loc[:periodo-1, "ema"] = np.nan
        #print(df)
        
        # Calcular cuántas velas cierran arriba y abajo de la EMA9
        total = len(df) - periodo

        # Velas por encima de la EMA9
        arriba = (df["closePrice"].astype(float) > df["ema"]).sum()

        # Velas por debajo de la EMA9
        abajo = (df["closePrice"].astype(float) < df["ema"]).sum()

        # Porcentajes
        pct_arriba = arriba / total * 100
        pct_abajo  = abajo / total * 100
        return pct_arriba > unbral or pct_abajo > unbral

    
    except Exception as e:
        print(f"\nERROR EN LA FUNCIÓN tendencia_954()\n{e}")
# ------------------------------------------------

#FUNCIÓN QUE ENVIA LAS ALERTAS
#------------------------------------------------
def alertas(tick):
    try:
        
        porcentaje_precios = porcentaje_precio(tick, temporalidad, cantidad_velas)
        
        if abs(porcentaje_precios) > variacion_precio:
            volumen = volumen_24h(tick)
            if volumen >= volumen24h:
                if exchange == "BYBIT" and (tendencia_954(exchange=exchange, symbol=tick, temporalidad="1", cantidad_velas=200, periodo=9, unbral=80) or 
                                            tendencia_954(exchange=exchange, symbol=tick, temporalidad="1", cantidad_velas=200, periodo=54, unbral=80) or
                                            tendencia_954(exchange=exchange, symbol=tick, temporalidad="5", cantidad_velas=200, periodo=9, unbral=80) or
                                            tendencia_954(exchange=exchange, symbol=tick, temporalidad="5", cantidad_velas=200, periodo=54, unbral=80)) or (
                exchange == "BINANCE" and (tendencia_954(exchange=exchange, symbol=tick, temporalidad=client.KLINE_INTERVAL_1MINUTE, cantidad_velas=200, periodo=9, unbral=80) or 
                                            tendencia_954(exchange=exchange, symbol=tick, temporalidad=client.KLINE_INTERVAL_1MINUTE, cantidad_velas=200, periodo=54, unbral=80) or
                                            tendencia_954(exchange=exchange, symbol=tick, temporalidad=client.KLINE_INTERVAL_5MINUTE, cantidad_velas=200, periodo=9, unbral=80) or
                                            tendencia_954(exchange=exchange, symbol=tick, temporalidad=client.KLINE_INTERVAL_5MINUTE, cantidad_velas=200, periodo=54, unbral=80))):
                    
                    # BAJISTA
                    if porcentaje_precios < 0:
                        texto_audio("Movimiento bajista en " + str(tick))
                        reproducir_audio('alerta_voz.mp3')
                        print(Fore.RED + "MOVIMIENTO BAJISTA" + Fore.RESET + ": ", tick)
                        print("Variación del precio:", str(porcentaje_precios) + "%")
                        print("Volumen en 24H:", formato_abreviado(volumen))
                        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                        print("")
                        return True

                    
                    # ALCISTA
                    if porcentaje_precios > 0:
                        texto_audio("Movimiento alcista en " + str(tick))
                        reproducir_audio('alerta_voz.mp3')
                        print(Fore.GREEN + "MOVIMIENTO ALCISTA" + Fore.RESET + ": ", tick)
                        print("Variación del precio:", str(porcentaje_precios) + "%")
                        print("Volumen en 24H:", formato_abreviado(volumen))
                        print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                        print("")
                        return True

    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE ENVIA LAS ALERTAS. (alertas())")
        print(e)
        print("")
#------------------------------------------------


# PROGRAMA PRINCIPAL
#'''
calientes = []
mas_calientes = [{"apariciones"}]
while iniciar:
        try:
            ticks = buscar_ticks()
            print("")
            print("PARÁMETROS DE BÚSQUEDA:")
            print("Exchange:", exchange)
            print("Variación del precio:", str(variacion_precio)+"%")
            print("Volumen mínimo en 24H:", formato_abreviado(volumen24h))
            print("")
            print("Buscando en", len(ticks), "monedas disponibles...")
            print("")
            print(Counter(calientes).most_common(5))
            print("")
            oi = coinalyze()
            for tick in ticks:
                if coinalyzecom and tick.split("USDT")[0] in str(oi[0]['MONEDA'].values).upper() or tick.split("USDT")[0] in str(oi[1]['MONEDA'].values).upper():
                    alerta = alertas(tick)
                    if alerta:
                        calientes.append(tick.split("USDT")[0])
                        print(Counter(calientes).most_common(5))
                        print("")
                    time.sleep(tiempo_de_iteracion)
                if not coinalyzecom:
                    alerta = alertas(tick)
                    if alerta:
                        calientes.append(tick.split("USDT")[0])
                        print(Counter(calientes).most_common(5))
                        print("")
                    time.sleep(tiempo_de_iteracion)
            print("Siguiente búsqueda en", tiempo_de_espera, "Segundos...")
            time.sleep(tiempo_de_espera)
        
        except Exception as e:
            try:
                texto_audio("Error en la búsqueda, esperando " + str(tiempo_recuperacion) + " Segundos...")
                print("ERROR EN LA BUSQUEDA")
                print(e)
                print("Esperando tiempo de recuperación.", tiempo_recuperacion, "Segundos...")
                print("")
                reproducir_audio('alerta_voz.mp3')
                time.sleep(tiempo_recuperacion)
            except Exception as e:
                pass
#'''
