import future
import soportes_resistencias
import pygame
from gtts import gTTS
import asyncio
import json
import time

# PARAMETROS
# ----------
parametros = json.load(open('future/estrategias/doble_cardiaco/parametros.json'))
exchange = parametros['exchange']
symbol = parametros['symbol']
temporalidad = parametros['temporalidad']
cantidad_velas = parametros['cantidad_velas']
rango = parametros['rango']
# ----------

# Función que analiza los rechazos en Soportes y Resistencias
# -----------------------------------------------------------
def mas_rechazados(exchange=exchange, symbol=symbol, temporalidad=temporalidad, cantidad_velas=cantidad_velas):
    try:

        # Obtener Soportes y Resistencias
        sr = soportes_resistencias.soportes_resistencias(exchange=exchange, symbol=symbol, temporalidad=temporalidad, cantidad_velas=cantidad_velas)
        
        # DataFrame
        df = sr[2]

        # Precio Actual
        precio_actual = future.precio_actual_activo(exchange=exchange, symbol=symbol)

        # SOPORTES
        soportes = []
        for s_r in sr[0]:
            if s_r < precio_actual:
                soportes.append(s_r)
        for s_r in sr[1]:
            if s_r < precio_actual:
                soportes.append(s_r)
        
        # Contar los rechazos a los soportes
        rechazos_soportes = []
        for soporte in soportes:
            rechazos = []
            for index, vela in df.iterrows():
                
                # Rechazo Tipo 1 Mechazo cerrando dentro del rango
                if vela['low']<=soporte*1.001 and vela['open']>=soporte*0.999 and vela['close']>soporte:
                    rechazos.append(str(index))
                
                # Rechazo Tipo 2 Mechazo cerrando muy cerca del borde del rango
                if vela['open']>soporte and soporte*0.999<=vela['close']<=soporte*1.001 and abs(vela['low']-vela['close'])>0.5*abs(vela['close']-vela['open']):
                    rechazos.append(str(index))
                
                # Rechazo Tipo 3 Regreso al rango después de 3 velas
                pos_actual = df.index.get_loc(index)
                if pos_actual < len(df.index)-3:
                    if vela['open']>soporte and vela['close']<=soporte*1.001 and df.iloc[pos_actual+3]['close']>soporte:
                        
                        # Evitar que cuente el mismo rechazo
                        if str(index) not in rechazos:
                            rechazos.append(str(index))
            
            rechazos_soportes.append({"Soporte": soporte, "Rechazos": rechazos})
        
        # RESISTENCIAS
        resistencias = []
        for s_r in sr[0]:
            if s_r > precio_actual:
                resistencias.append(s_r)
        for s_r in sr[1]:
            if s_r > precio_actual:
                resistencias.append(s_r)

        # Contar los rechazos a las resistencias
        rechazos_resistencias = []
        for resistencia in resistencias:
            rechazos = []
            for index, vela in df.iterrows():
                
                # Rechazo Tipo 1 Mechazo cerrando dentro del rango
                if vela['high']>=resistencia*0.999 and vela['open']<=resistencia*1.001 and vela['close']<resistencia:
                    rechazos.append(str(index))
                
                # Rechazo Tipo 2 Mechazo cerrando muy cerca del borde del rango
                if vela['open']<resistencia and resistencia*0.999<=vela['close']<=resistencia*1.001 and abs(vela['high']-vela['close'])>0.5*abs(vela['close']-vela['open']):
                    rechazos.append(str(index))
                
                # Rechazo Tipo 3 Regreso al rango después de 3 velas
                pos_actual = df.index.get_loc(index)
                if pos_actual < len(df.index)-3:
                    if vela['open']<resistencia and vela['close']>=resistencia*0.999 and df.iloc[pos_actual+3]['close']<resistencia:
                        
                        # Evitar que cuente el mismo rechazo
                        if str(index) not in rechazos:
                            rechazos.append(str(index))
            
            rechazos_resistencias.append({"Resistencia": resistencia, "Rechazos": rechazos})

        # Soporte mas rechazado
        soporte_mas_rechazado = {}
        if rechazos_soportes != []:
            soporte_mas_rechazado = rechazos_soportes[0]
            for soporte in rechazos_soportes:
                if len(soporte['Rechazos']) > len(soporte_mas_rechazado['Rechazos']):
                    soporte_mas_rechazado = soporte
            #print(json.dumps(soporte_mas_rechazado,indent=2))
            #print("")
            
        # Resistencia mas rechazada
        resistencia_mas_rechazado = {}
        if rechazos_resistencias != []:
            resistencia_mas_rechazado = rechazos_resistencias[0]
            for resistencia in rechazos_resistencias:
                if len(resistencia['Rechazos']) > len(resistencia_mas_rechazado['Rechazos']):
                    resistencia_mas_rechazado = resistencia
            #print(json.dumps(resistencia_mas_rechazado,indent=2))
            #print("")
            
        return soporte_mas_rechazado, resistencia_mas_rechazado
        
    except Exception as e:
        print("ERROR ANALIZANDO LOS RECHAZOS")
        print(e)
        print("")
# -----------------------------------------------------------

# Función que detecta un rango útil para el Doble Cariaco
# -------------------------------------------------------
def rango_cardiaco():
    try:
        ticks = future.buscar_ticks(exchange=exchange)
        if symbol != "":
            ticks = []
            ticks.append(symbol.upper()+"USDT")
        for tick in ticks:
            try:

                # Eliminar la palabra "_24" del tick
                if "_24" in tick:
                    tick = tick.split("_24")[0]
                # Eliminar la palabra "USDT" del tick
                tick = tick[0:-4]

                # Obtener el Soporte y la Resistencia mas rechazados
                sr = mas_rechazados(symbol=tick)
                
                # 
                if sr[0] != {} and sr[1] != {}:
                    rechazos_soporte = len(sr[0]["Rechazos"])
                    rechazos_resistenca = len(sr[1]["Rechazos"])
                    porcentaje_soporte = 100*rechazos_soporte/(rechazos_soporte+rechazos_resistenca)
                    porcentaje_resistencia = 100*rechazos_resistenca/(rechazos_soporte+rechazos_resistenca)
                    distancia = 100*(sr[1]['Resistencia'] - sr[0]['Soporte'])/sr[0]['Soporte']
                    if (rechazos_soporte>3 and rechazos_resistenca>3) and ((45 <= porcentaje_soporte <= 55) or (45 <= porcentaje_resistencia <= 55)) and (rango[0] <= distancia <= rango[1]):
                        print("")
                        print(tick)
                        print("Temporalidad:", temporalidad, "Cantidad de Velas:", cantidad_velas)
                        texto_audio(f"Rango Detectado en {tick}")
                        asyncio.run(reproducir_audio("alerta_voz.mp3"))
                        print("Rango Detectado")
                        print("Soporte:", sr[0]['Soporte'], "Rechazos:", rechazos_soporte, f"Porcentaje: {round(porcentaje_soporte,2)}%")
                        print("Resistencia:", sr[1]['Resistencia'], "Rechazos:", rechazos_resistenca, f"Porcentaje: {round(porcentaje_resistencia,2)}%")
                        print(f"Distancia: {round(distancia,2)}%")
                        print("")
            
            except Exception as e:
                pass
    except Exception as e:
        print("ERROR BUSCANDO RANGOS")
        print(e)
        print(tick)
        print(sr)
        print("")
# -------------------------------------------------------

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

while True:
    print("")
    print("Buscando Rango...")
    rango_cardiaco()