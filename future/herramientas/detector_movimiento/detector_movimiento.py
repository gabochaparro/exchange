from binance.client import Client
from pybit.unified_trading import HTTP
import time
import pygame
from gtts import gTTS
from mutagen.mp3 import MP3
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
dato_correcto = False
while not dato_correcto:
    try:
        exchange = "BINANCE" #input("Introduce el exchange: ").upper()
        variacion_precio = 1 #float(input("Introduce la variación del precio: "))    # Variación en el precio (porcentaje)
        volumen24h = 1000000*100 #int(input("Introduce el volumen en 24H (M): "))          # Volumen en 24 horas
        dato_correcto = True
    
    except Exception as e:
        print("DATO INCORRECTO!")
        print("")
tiempo_de_espera = 2                                # Tiempo de espera para una nueva busqueda
tiempo_recuperacion = 3                             # Tiempo de recuperción después de un error
tiempo_de_iteracion = 0.1                           # Tiempo de iteracción entre cada tick
temporalidad = Client.KLINE_INTERVAL_1MINUTE        # Temporalidad
cantidad_velas = 5                                  # Cantidad de velas a considerar                                 
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


#FUNCIÓN QUE ENVIA LAS ALERTAS
#------------------------------------------------
def alertas(tick):
    try:
        
        porcentaje_precios = porcentaje_precio(tick, temporalidad, cantidad_velas)
        
        if abs(porcentaje_precios) > variacion_precio:
            volumen = volumen_24h(tick)
            if volumen >= volumen24h:
                
                # SHORT
                if porcentaje_precios < 0:
                    print(Fore.RED + "MOVIMIENTO BAJISTA" + Fore.RESET + ": ", tick)
                    print("Variación del precio:", str(porcentaje_precios) + "%")
                    print("Volumen en 24H:", formato_abreviado(volumen))
                    print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                    print("")
                    texto_audio("Movimiento bajista en " + str(tick))
                    reproducir_audio('alerta_voz.mp3')

                
                # LONG
                if porcentaje_precios > 0:
                    print(Fore.GREEN + "MOVIMIENTO ALCISTA" + Fore.RESET + ": ", tick)
                    print("Variación del precio:", str(porcentaje_precios) + "%")
                    print("Volumen en 24H:", formato_abreviado(volumen))
                    print(datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"))
                    print("")
                    texto_audio("Movimiento alcista en " + str(tick))
                    reproducir_audio('alerta_voz.mp3')

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
            print("Volumen mínimo en 24H:", formato_abreviado(volumen24h))
            print("")
            ticks = buscar_ticks()
            print("Buscando en", len(ticks), "monedas disponibles...")
            print("")
            for tick in ticks:
                i = i + 1
                #print (i, tick)
                alertas(tick)
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