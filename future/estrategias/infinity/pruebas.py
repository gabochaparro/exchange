import json
import os
import paramiko  # Para conexión SFTP

# Configuración global para EC2
EC2_HOST = "ec2-15-228-57-72.sa-east-1.compute.amazonaws.com"  # Dirección de tu instancia EC2
EC2_PORT = 22  # Puerto SSH (22 por defecto)
EC2_USER = "ubuntu"  # Usuario para conectar a EC2
EC2_KEY_PATH = "future/estrategias/infinity/clave_pen_ec2_01.pem"  # Ruta a tu llave privada
REMOTE_DIRECTORY = "/home/ubuntu/exchange/future/estrategias/infinity"  # Directorio en EC2 donde están los parametros iniciales
REMOTE_DIRECTORY_LIVE = "/home/ubuntu/exchange/future/estrategias/infinity/parametros"  # Directorio en EC2 donde están los parametros en vivo

# Variables globales
ruta_archivo = None

# Función para listar archivos JSON en el directorio remoto
def listar_archivos_remotos():
    try:
        # Conexión SFTP
        clave = paramiko.RSAKey.from_private_key_file(EC2_KEY_PATH)
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(EC2_HOST, port=EC2_PORT, username=EC2_USER, pkey=clave)

        sftp = cliente.open_sftp()
        archivos = sftp.listdir(REMOTE_DIRECTORY)
        archivos_json = [f for f in archivos if f.endswith(".json")]
        sftp.close()
        cliente.close()

        return archivos_json
    except Exception as e:
        print("Error", f"No se pudo listar los archivos remotos: {e}")
        return []

# Función para descargar un archivo remoto
def descargar_archivo_remoto(ruta_remota, nombre_archivo):
    global ruta_archivo
    try:
        # Conexión SFTP
        clave = paramiko.RSAKey.from_private_key_file(EC2_KEY_PATH)
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(EC2_HOST, port=EC2_PORT, username=EC2_USER, pkey=clave)

        sftp = cliente.open_sftp()
        ruta_local = os.path.join(os.getcwd(), nombre_archivo)
        print(ruta_local)
        ruta_archivo = ruta_local
        sftp.get(ruta_remota, ruta_local)  # Descargar archivo
        sftp.close()
        cliente.close()
        
        print("")
        print(f"Archivo {nombre_archivo} descargado correctamente.")
    except Exception as e:
        print("Error", f"No se pudo descargar el archivo remoto: {e}")
        print("")

# Función para subir un archivo modificado
def subir_archivo_remoto():
    if not ruta_archivo:
        print("Advertencia", "No hay ningún archivo cargado para guardar.")
        return

    nombre_archivo = os.path.basename(ruta_archivo)
    ruta_remota = f"{REMOTE_DIRECTORY}/{nombre_archivo}"

    try:
        # Conexión SFTP
        clave = paramiko.RSAKey.from_private_key_file(EC2_KEY_PATH)
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(EC2_HOST, port=EC2_PORT, username=EC2_USER, pkey=clave)

        sftp = cliente.open_sftp()
        sftp.put(ruta_archivo, ruta_remota)  # Subir archivo
        sftp.close()
        cliente.close()

        print("")
        print(f"Archivo {nombre_archivo} guardado en el servidor correctamente.")
    except Exception as e:
        print("Error", f"No se pudo guardar el archivo remoto: {e}")
        print("")

parametros = input("Parametros o Live? (P/L): ").upper()
if parametros == "L":
    directorio_remoto = REMOTE_DIRECTORY_LIVE
else:
    directorio_remoto = REMOTE_DIRECTORY
archivos = listar_archivos_remotos()
print(json.dumps(archivos,indent=2))
archivo = input('Introduce el nombre del archivo: ')
descargar_archivo_remoto(f'{directorio_remoto}/{archivo}',archivo)
input('Presiona Enter para subir el archivo')
subir_archivo_remoto()