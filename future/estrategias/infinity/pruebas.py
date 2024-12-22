import json
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os
import paramiko  # Biblioteca para conectar con la instancia EC2

# Configuración global para conexión a EC2
EC2_CONFIG = {
    'hostname': 'ec2-XX-XXX-XXX-XXX.compute-1.amazonaws.com',  # Reemplaza con tu hostname
    'username': 'ec2-user',  # Reemplaza con tu usuario
    'key_filename': '/ruta/a/tu/clave.pem'  # Ruta al archivo PEM
}

# Variables globales
data = {}
ruta_archivo = None
ultima_modificacion = None
entries = {}
botones_booleanos = {}
conexion_ec2 = None
archivo_remoto = None  # Ruta del archivo JSON en la instancia EC2

# Conectar a EC2

def conectar_ec2():
    global conexion_ec2
    try:
        conexion_ec2 = paramiko.SSHClient()
        conexion_ec2.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        conexion_ec2.connect(**EC2_CONFIG)
        print("Conexión a EC2 exitosa.")
    except Exception as e:
        print(f"Error al conectar a EC2: {e}")

# Descargar archivo JSON desde EC2
def descargar_archivo_ec2(ruta_remota, ruta_local):
    try:
        sftp = conexion_ec2.open_sftp()
        sftp.get(ruta_remota, ruta_local)
        sftp.close()
        print("Archivo descargado exitosamente desde EC2.")
    except Exception as e:
        print(f"Error al descargar archivo desde EC2: {e}")

# Subir archivo JSON a EC2
def subir_archivo_ec2(ruta_local, ruta_remota):
    try:
        sftp = conexion_ec2.open_sftp()
        sftp.put(ruta_local, ruta_remota)
        sftp.close()
        print("Archivo subido exitosamente a EC2.")
    except Exception as e:
        print(f"Error al subir archivo a EC2: {e}")

# Función para cargar el archivo JSON
def cargar_json():
    global data, ruta_archivo, ultima_modificacion, archivo_remoto
    try:
        opcion = messagebox.askquestion("Origen del archivo", "¿Quieres cargar un archivo desde EC2?")

        if opcion == "yes":
            archivo_remoto = filedialog.askstring("Ruta remota", "Introduce la ruta del archivo JSON en EC2:")
            ruta_local_temp = f"temp_{os.path.basename(archivo_remoto)}"
            descargar_archivo_ec2(archivo_remoto, ruta_local_temp)
            ruta_archivo = ruta_local_temp
        else:
            ruta_archivo = filedialog.askopenfilename(
                title="Seleccionar archivo JSON",
                filetypes=[("Archivos JSON", "*.json")]
            )

        if ruta_archivo:
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                data = json.load(f)
            ultima_modificacion = os.path.getmtime(ruta_archivo)
            actualizar_interfaz()
            messagebox.showinfo("Carga exitosa", "Archivo cargado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

# Función que actualiza la interfaz
def actualizar_interfaz():
    for widget in frame_editor.winfo_children():
        widget.destroy()
    entries.clear()
    botones_booleanos.clear()

    for i, (clave, valor) in enumerate(data.items()):
        tk.Label(frame_editor, text=f"{clave}:", anchor="w", width=25).grid(row=i, column=0, padx=5, pady=5)

        if isinstance(valor, bool):
            btn_toggle = tk.Button(
                frame_editor, text="Sí" if valor else "No",
                command=lambda c=clave: toggle_boolean(c)
            )
            btn_toggle.grid(row=i, column=1, padx=5, pady=5)
            botones_booleanos[clave] = btn_toggle
        else:
            entry = tk.Entry(frame_editor, width=30)
            entry.insert(0, str(valor))
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[clave] = entry

# Función para alternar valores booleanos
def toggle_boolean(clave):
    data[clave] = not data[clave]
    botones_booleanos[clave].config(text="Sí" if data[clave] else "No")

# Función para guardar cambios en el archivo JSON
def guardar_json():
    global archivo_remoto
    try:
        for clave, entry in entries.items():
            valor = entry.get()
            try:
                data[clave] = json.loads(valor)  # Convertir al tipo adecuado
            except:
                data[clave] = valor

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        if archivo_remoto:
            subir_archivo_ec2(ruta_archivo, archivo_remoto)

        messagebox.showinfo("Guardado exitoso", "Archivo guardado correctamente.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

# Función para monitorear cambios en el archivo JSON
def monitorear_cambios():
    global ultima_modificacion, ruta_archivo, data
    while True:
        if ruta_archivo:
            try:
                mod_time = os.path.getmtime(ruta_archivo)
                if mod_time != ultima_modificacion:
                    ultima_modificacion = mod_time
                    with open(ruta_archivo, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    ventana.after(0, actualizar_interfaz)
            except Exception as e:
                print(f"Error monitoreando el archivo: {e}")
        time.sleep(1)

# Conectar a EC2 al inicio
conectar_ec2()

# Configurar la ventana principal
ventana = tk.Tk()
ventana.title("Editor de JSON - Local y EC2")
ventana.geometry("600x400")

# Botones de carga y guardado
boton_cargar = tk.Button(ventana, text="Cargar", command=cargar_json)
boton_cargar.pack(pady=10)

boton_guardar = tk.Button(ventana, text="Guardar", command=guardar_json)
boton_guardar.pack(pady=10)

# Frame para el editor
frame_editor = tk.Frame(ventana)
frame_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Iniciar monitoreo en un hilo separado
hilo_monitoreo = threading.Thread(target=monitorear_cambios, daemon=True)
hilo_monitoreo.start()

# Ejecutar la aplicación
ventana.mainloop()
