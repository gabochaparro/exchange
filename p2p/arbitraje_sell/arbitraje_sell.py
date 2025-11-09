import binance_p2p as anuncios
import json
import time


# FUNCIÓN QUE GENERA UN ARCHIVO DE AUDIO A PARTIR DE UN TEXTO
#------------------------------------------------------------
def texto_audio(texto):
    try:
         # Importar librerias
        from gtts import gTTS
        from mutagen.mp3 import MP3
        
        # Elegir el idioma
        idioma = "es"
        
        # Indicar el texto, idioma y velocidad de lectura
        tts = gTTS(text=texto, lang=idioma)
        
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
def reproducir_audio(audio):
    try: 
         # Importar librerias
        import pygame
        from mutagen.mp3 import MP3
        
        # Duracion del audio
        duracion = MP3(audio).info.length
        
        # Inicializar el mixer
        pygame.mixer.init()

        # Cargar el audio
        pygame.mixer.music.load(audio)

        # Reproducir el audio
        pygame.mixer.music.play()
        time.sleep(duracion)
        pygame.mixer.music.unload()  # Liberar el archivo después de reproducir
        pygame.mixer.quit()  # Finalizar el mixer
    
    except Exception as e:
        print("ERROR EN LA FUNCIÓN QUE REPRODUCE AUDIO")
        print(e)
# -------------------------------

# Variables principales
ganancia = 1                                    # Ganancia del arbitraje
bancos = ["Nequi", "BancolombiaSA"]             # Bancos a buscar
monto = 33600                                   # Monto de los anuncios mas baratos
comision = 0.35                                # Comision por publicar
buscar = True

while buscar:
    try:
        # Obtener el anuncio mas caro
        anuncio_caro = anuncios.obtener_anuncios(symbol="USDT", fiat="COP", tipo="SELL", monto=0, bancos=bancos)

        # Obtener el anuncio mas barato
        anuncio_barato = anuncios.obtener_anuncios(symbol="USDT", fiat="COP", tipo="SELL", monto=monto, bancos=bancos)

        # Relajar la API por error 429
        if str(anuncio_caro) == "429" or str(anuncio_barato) == "429":
            tiempo_espera = 60*10 # 10 minutos por si la API da error
            print("Eserando 10 minutos")
            time.sleep(tiempo_espera)
            continue
        
        # Preparar los precios
        print(json.dumps([anuncio_caro, anuncio_barato], indent=2))
        precio_caro = float(anuncio_caro[0]['precio'])
        precio_barato = float(anuncio_barato[0]['precio'])
        precio_anuncio = (precio_barato + 0.01)
        precio_anuncio_real = precio_anuncio*(1+comision/100) # Con la comision en bs
        precio_oportunidad = precio_anuncio_real*(1+ganancia/100)
        ganancia_actual = 100*(precio_caro - precio_anuncio_real)/precio_anuncio_real
        
        # Verificando oportunidad
        print(f"Precio oportunidad mayor a: {round(precio_oportunidad,3)}")
        print(f"Ganancia actual: {round(ganancia_actual,2)}%")
        if precio_caro >= precio_oportunidad:
            print("!!!OPORTUNIDAD DE ARBITRAJE!!!")
            texto_audio("Oportunidad de arbitraje detectada")
            reproducir_audio("alerta_voz.mp3")
        
        # Retraso para evitar sanciones de la API de Binance
        time.sleep(1*60)
    
    except Exception as e:
        print(f"ERROR EN EL CICLO\n{e}")