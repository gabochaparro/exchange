import json
import os
import paramiko  # Para conexión SFTP
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Configuración global para EC2
EC2_HOST = "ec2-15-228-57-72.sa-east-1.compute.amazonaws.com"  # Dirección de tu instancia EC2
EC2_PORT = 22  # Puerto SSH (22 por defecto)
EC2_USER = "ubuntu"  # Usuario para conectar a EC2
EC2_KEY_PATH = os.path.dirname(__file__)+"/future/estrategias/infinity/clave_pen_ec2_01.pem"  # Ruta a tu llave privada
PARAMETROS = "/home/ubuntu/exchange/future/estrategias/infinity"  # Directorio en EC2 donde están los parametros iniciales
PARAMETROS_LIVE = "/home/ubuntu/exchange/future/estrategias/infinity/parametros"  # Directorio en EC2 donde están los parametros en vivo
SALIDA = "/home/ubuntu/exchange/future/estrategias/infinity/salida" # Directorio en EC2 donde están las salidas

# Variables globales
ruta_archivo = None

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
        messagebox.showerror("Error", f"No se pudo listar los archivos remotos: {e}")
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
        ruta_local = f"{os.path.dirname(__file__)}/future/estrategias/infinity/salida/{nombre_archivo}"
        ruta_archivo = ruta_local
        sftp.get(ruta_remota, ruta_local)  # Descargar archivo
        sftp.close()
        cliente.close()

        messagebox.showinfo("Éxito", f"Archivo {nombre_archivo} descargado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo descargar el archivo remoto: {e}")

# Función para subir un archivo modificado
def subir_archivo_remoto(directorio_remoto):
    if not ruta_archivo:
        messagebox.showwarning("Advertencia", "No hay ningún archivo cargado para guardar.")
        return

    nombre_archivo = os.path.basename(ruta_archivo)
    ruta_remota = f"{directorio_remoto}/{nombre_archivo}"

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

        messagebox.showinfo("Éxito", f"Archivo {nombre_archivo} guardado en el servidor correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo remoto: {e}")

# Función principal para la GUI
def main():
    def cargar_archivos():
        parametros = opcion_parametros.get()
        if parametros == "Live":
            directorio_remoto = PARAMETROS_LIVE
        elif parametros == "Iniciales":
            directorio_remoto = PARAMETROS
        else:
            directorio_remoto = SALIDA
        archivos = listar_archivos_remotos(directorio_remoto)
        lista_archivos_var.set(archivos)

    def descargar_archivo():
        parametros = opcion_parametros.get()
        if parametros == "Live":
            directorio_remoto = PARAMETROS_LIVE
        elif parametros == "Iniciales":
            directorio_remoto = PARAMETROS
        else:
            directorio_remoto = SALIDA
        seleccion = lista_archivos.curselection()  # Obtener el índice seleccionado
        if seleccion:
            archivo = lista_archivos.get(seleccion[0])  # Obtener el archivo seleccionado
            descargar_archivo_remoto(f"{directorio_remoto}/{archivo}", archivo)
        else:
            messagebox.showwarning("Advertencia", "Por favor, selecciona un archivo para descargar.")


    def subir_archivo():
        parametros = opcion_parametros.get()
        directorio_remoto = PARAMETROS_LIVE if parametros == "Live" else PARAMETROS
        subir_archivo_remoto(directorio_remoto)

    root = tk.Tk()
    root.title("Parametros EC2")

    frame = ttk.Frame(root, padding=10)
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    ttk.Label(frame, text="Tipo de parámetros:").grid(row=0, column=0, sticky=tk.W)

    opcion_parametros = tk.StringVar(value="Parametros_Iniciales")
    ttk.Radiobutton(frame, text="Parametros Iniciales", variable=opcion_parametros, value="Iniciales").grid(row=1, column=0, sticky=tk.W)
    ttk.Radiobutton(frame, text="Parametros Vivos", variable=opcion_parametros, value="Live").grid(row=2, column=0, sticky=tk.W)
    ttk.Radiobutton(frame, text="Salida", variable=opcion_parametros, value="Salida").grid(row=3, column=0, sticky=tk.W)

    ttk.Button(frame, text="Selecionar Archivos", command=cargar_archivos).grid(row=4, column=0, pady=5, sticky=tk.W)

    lista_archivos_var = tk.StringVar(value=[])
    lista_archivos = tk.Listbox(frame, listvariable=lista_archivos_var, height=10, width=50)
    lista_archivos.grid(row=5, column=0, pady=5, sticky=tk.W)

    ttk.Button(frame, text="Descargar Archivo", command=descargar_archivo).grid(row=6, column=0, pady=5, sticky=tk.W)
    ttk.Button(frame, text="Subir Archivo", command=subir_archivo).grid(row=7, column=0, pady=5, sticky=tk.W)

    root.mainloop()

if __name__ == "__main__":
    main()
