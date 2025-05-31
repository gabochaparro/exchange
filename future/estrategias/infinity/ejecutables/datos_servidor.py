import json
import os
import paramiko  # Para conexión SFTP
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
import glob

# Configuración global para EC2
EC2_HOST = "ec2-15-228-57-72.sa-east-1.compute.amazonaws.com"  # Dirección de tu instancia EC2
EC2_PORT = 22  # Puerto SSH (22 por defecto)
EC2_USER = "ubuntu"  # Usuario para conectar a EC2
EC2_KEY_PATH = os.path.dirname(__file__)+"/future/estrategias/infinity/clave_pen_ec2_01.pem"  # Ruta a tu llave privada
CREDENCIALES_REMOTO = "/home/ubuntu/exchange/future/estrategias/infinity" # Directorio en EC2 donde están las credenciales
PARAMETROS_REMOTO = "/home/ubuntu/exchange/future/estrategias/infinity"  # Directorio en EC2 donde están los parametros iniciales
PARAMETROS_LIVE_REMOTO = "/home/ubuntu/exchange/future/estrategias/infinity/parametros"  # Directorio en EC2 donde están los parametros en vivo
SALIDA_REMOTO = "/home/ubuntu/exchange/future/estrategias/infinity/salida" # Directorio en EC2 donde están las salidas

# Directorios locales
CREDENCIALES_LOCAL = os.path.dirname(__file__)+"/future/estrategias/infinity"
PARAMETROS_LOCAL = os.path.dirname(__file__)+"/future/estrategias/infinity"
PARAMETROS_LIVE_LOCAL = os.path.dirname(__file__)+"/future/estrategias/infinity/parametros"
SALIDA_LOCAL = os.path.dirname(__file__)+"/future/estrategias/infinity/salida"

# Función para listar archivos JSON en el directorio remoto
def listar_archivos_remotos(directorio_remoto):
    try:
        # Conexión SFTP
        clave = paramiko.RSAKey.from_private_key_file(EC2_KEY_PATH)
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(EC2_HOST, port=EC2_PORT, username=EC2_USER, pkey=clave)

        sftp = cliente.open_sftp()
        archivos = sftp.listdir(directorio_remoto)
        archivos_json = [f for f in archivos if f.endswith(".json")]
        sftp.close()
        cliente.close()

        return archivos_json
    except Exception as e:
        print("Error", f"No se pudo listar los archivos remotos: {e}")
        return []

# Función para descargar un archivo remoto
def descargar_archivo_remoto(ruta_remota, ruta_local, nombre_archivo):
    global ruta_archivo
    try:

        # Conexión SFTP
        clave = paramiko.RSAKey.from_private_key_file(EC2_KEY_PATH)
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(EC2_HOST, port=EC2_PORT, username=EC2_USER, pkey=clave)

        sftp = cliente.open_sftp()
        sftp.get(f"{ruta_remota}/{nombre_archivo}", f"{ruta_local}/{nombre_archivo}")  # Descargar archivo
        sftp.close()
        cliente.close()

        print("")
        print(f"Archivo {nombre_archivo} descargado correctamente.")
        print("")
        return "OK"
    except Exception as e:
        print("Error", f"No se pudo descargar el archivo remoto: {e}")

# Función para subir un archivo modificado
def subir_archivo_remoto(directorio_remoto, ruta_local, nombre_archivo):

    ruta_local = f"{ruta_local}/{nombre_archivo}"
    ruta_remota = f"{directorio_remoto}/{nombre_archivo}"

    try:
        # Conexión SFTP
        clave = paramiko.RSAKey.from_private_key_file(EC2_KEY_PATH)
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(EC2_HOST, port=EC2_PORT, username=EC2_USER, pkey=clave)

        sftp = cliente.open_sftp()
        sftp.put(ruta_local, ruta_remota)  # Subir archivo
        sftp.close()
        cliente.close()

        print("Éxito", f"Archivo {nombre_archivo} guardado en el servidor correctamente.")
        return "OK"
    except Exception as e:
        print("Error", f"No se pudo guardar el archivo remoto: {e}")

# Función para mantener actualizadas las salidas
def salidas_actualizadas():

    # Usa glob para obtener todos los archivos dentro de la carpeta
    archivos = glob.glob(f'{SALIDA_LOCAL}/*')

    # Elimina cada archivo en la carpeta
    for archivo in archivos:
        try:
            os.remove(archivo)
            print(f"{archivo} eliminado exitosamente.")
        except IsADirectoryError:
            print(f"{archivo} es una carpeta, omitiendo.")
        except FileNotFoundError:
            print(f"{archivo} no existe.")
        except PermissionError:
            print(f"No tienes permisos para eliminar {archivo}.")

    while True:
        try:
            salidas_remotas = listar_archivos_remotos(SALIDA_REMOTO)
            for archivo in salidas_remotas:
                descargar_archivo_remoto(SALIDA_REMOTO,SALIDA_LOCAL,archivo)
        
        except Exception as e:
            print("ERROR ACTUALIZANDO LAS SALIDAS")
            print(e)
            print("")

# Función para mantener actualizado los parametros caliente
def parametros_actualizados():
    try:
        # Decargar parametros uniciales remoto
        descargar_archivo_remoto(PARAMETROS_REMOTO,PARAMETROS_LOCAL,"parametros_infinity_2.0.json")
        
        # Abrir el archivo parametros.json y cargar su contenido
        parametros_iniciales = json.load(open(f"{PARAMETROS_LOCAL}/parametros_infinity_2.0.json","r"))

        #  Especifica la ruta de la carpeta parametros
        carpeta_parametros = f'{PARAMETROS_LIVE_LOCAL}/*'

        # Usa glob para obtener todos los archivos dentro de la carpeta
        archivos = glob.glob(carpeta_parametros)

        # Elimina cada archivo en la carpeta
        for archivo in archivos:
            try:
                if parametros_iniciales['inverso']:
                    if f"{parametros_iniciales['activo'].upper()}_{parametros_iniciales['exchange'].upper()}_INVERSO" in archivo:
                        os.remove(archivo)
                        print(f"{archivo} eliminado exitosamente.")
                else:
                    if f"{parametros_iniciales['activo'].upper()}_{parametros_iniciales['exchange'].upper()}_LINEAL" in archivo:
                        os.remove(archivo)
                        print(f"{archivo} eliminado exitosamente.")
            except IsADirectoryError:
                print(f"{archivo} es una carpeta, omitiendo.")
            except FileNotFoundError:
                print(f"{archivo} no existe.")
            except PermissionError:
                print(f"No tienes permisos para eliminar {archivo}.")

        while True:
            parametros_calientes = listar_archivos_remotos(PARAMETROS_LIVE_REMOTO)
            for archivo in parametros_calientes:
                if parametros_iniciales['activo'].upper() in archivo:
                    if parametros_iniciales['inverso']:
                        if "INVERSO" in archivo:
                            descargar_archivo_remoto(PARAMETROS_LIVE_REMOTO,PARAMETROS_LIVE_LOCAL,archivo)
                    else:
                        if "LINEAL" in archivo:
                            descargar_archivo_remoto(PARAMETROS_LIVE_REMOTO,PARAMETROS_LIVE_LOCAL,archivo)

    except Exception as e:
        print("ERROR")
        print(e)
        print("")


'''
hilo_saida = threading.Thread(target=salidas_actualizadas, daemon=True)
hilo_saida.start()
hilo_parametros = threading.Thread(target=parametros_actualizados, daemon=True)
hilo_parametros.start()

while True:
    # Verificar que los hilos enten activos
    if not(hilo_saida.is_alive()):
        threading.Thread(target=salidas_actualizadas, daemon=True)
        hilo_saida.start()
    if not(hilo_parametros.is_alive()):
        threading.Thread(target=hilo_parametros, daemon=True)
        hilo_parametros.start()
#'''