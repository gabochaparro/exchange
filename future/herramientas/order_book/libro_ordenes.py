# FUNCIÓN QUE CALCULA LA ACUMULACIÓN DE ÓRDENES EN EL LIBRO DE ORDENES DE BINANCE
# Entradas: symbol="Activo a monitorear, ejempor 'BTC", umbral="Cantodad de dinero en millones, ejemplo 90"
# -------------------------------------------------------------------------------
def order_book(symbol, umbral):
    try:
        from binance.client import Client
        import pygame
        from mutagen.mp3 import MP3
        from gtts import gTTS
        import time
        from datetime import datetime


        binance_client = Client(
                                    api_key="",
                                    api_secret="",
                                    tld="com"
                                )


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
                
                #Escoger el tipo de voz
                voz = "female"
                
                # Indicar el texto, idioma y velocidad de lectura
                tts = gTTS(text=texto, lang=idioma, slow=False)
                
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
            except Exception as e:
                print("ERROR EN LA FUNCIÓN QUE REPRODUCE AUDIO")
                print(e)
        # -------------------------------

        # FUNCIÓN QUE ALERTA CUANDO UN ACTIVO ACUMULA CIERTA CANTIDAD DE ORDENES EN EL LIBRO DE ORDENES
        # ---------------------------------------------------------------------------------------------
        def alerta_ordenes(symbol, umbral):
            try:

                # Definir el simbolo
                symbol = symbol.upper()
                symbol = symbol+"USDT"

                # Obtener el precio actual
                precio_actual = float(binance_client.get_symbol_ticker(symbol=symbol)['price'])
                
                # Obtener las ordenes de compra
                libro_compras = binance_client.futures_order_book(symbol=symbol, limit=1000)['bids']

                # Decimales de la moneda
                decimales_moneda = len((libro_compras[0][0]).split(".")[1])

                cantidad_compra = 0
                for order in libro_compras:
                    cantidad_compra = cantidad_compra + float(order[1])

                if cantidad_compra*precio_actual > 1000000*umbral:
                    print("")
                    print("Acumulación de ordenes de compra")
                    print(f"{libro_compras[-1][0]} - {libro_compras[0][0]} ({round(float(libro_compras[0][0]) - float(libro_compras[-1][0]),decimales_moneda)})")
                    print(int(cantidad_compra), symbol.split("USDT")[0], ",", int(cantidad_compra*precio_actual), "USDT")
                    print(datetime.now().strftime('%Y-%m-%d - %I:%M:%S %p'))
                    print("")
                    texto_audio(f"Acumulación de órdenes de compra en {symbol.split('USDT')[0]}")
                    reproducir_audio("alerta_voz.mp3")

                # Obtener las ordenes de venta
                libro_ventas = binance_client.futures_order_book(symbol=symbol, limit=1000)['asks']

                cantidad_venta = 0
                for order in libro_ventas:
                    cantidad_venta = cantidad_venta + float(order[1])

                if cantidad_venta*precio_actual > 1000000*umbral:
                    print("")
                    print("Acumulación de ordenes de venta")
                    print(f"{libro_ventas[0][0]} - {libro_ventas[-1][0]} ({round(float(libro_ventas[-1][0]) - float(libro_ventas[0][0]),decimales_moneda)})")
                    print(int(cantidad_compra), symbol.split("USDT")[0], ",", int(cantidad_compra*precio_actual), "USDT")
                    print(datetime.now().strftime('%Y-%m-%d - %I:%M:%S %p'))
                    print("")
                    texto_audio(f"Acumulación de órdenes de venta en {symbol.split('USDT')[0]}")
                    reproducir_audio("alerta_voz.mp3")
            
            except Exception as e:
                print("ERROR EN LA FUNCIÓN alerta_ordenes()")
                print(e)
                print("")
        # ---------------------------------------------------------------------------------------------

        print("")
        print(f"Monitoreo del Order Book de {symbol}")
        print("")

        while True:
            alerta_ordenes(symbol=symbol,umbral=umbral)
            time.sleep(5.4)

    except Exception as e:
        print("ERROR EN LA FUNCIÓN order_book()")
        print(e)
        print("")
# -------------------------------------------------------------------------------

order_book("BTC",90)