import tkinter as tk
import json
import time
import threading
from datetime import datetime
import os
import tkinter.filedialog as filedialog

# Inicializamos una variable global para detectar cambios en el archivo
RUTA_JSON = ""
HASH_ARCHIVO_ACTUAL = None

# Colores personalizados
COLOR_FONDO = "#1e1e2f"
COLOR_TEXTO = "#e0e0e0"
COLOR_TITULO = "#ff9900"
COLOR_SECCION = "#29293d"
COLOR_BORDE = "#404056"
COLOR_POSITIVO = "#00ff00"
COLOR_NEGATIVO = "#ff0000"

# Crear ventana principal
root = tk.Tk()
root.title("Panel de Operaciones")
root.geometry("405x810")
root.configure(bg=COLOR_FONDO)

# Frame principal para información general
frame_principal = tk.Frame(root, bg=COLOR_FONDO)
frame_principal.pack(side="top", fill="x", padx=10, pady=5)

# Canvas para las operaciones
frame_con_canvas = tk.Frame(root, bg=COLOR_FONDO)
frame_con_canvas.pack(side="top", fill="both", expand=True)
canvas = tk.Canvas(frame_con_canvas, bg=COLOR_FONDO, highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)
scrollbar = tk.Scrollbar(frame_con_canvas, orient="vertical", command=canvas.yview, bg=COLOR_FONDO)
scrollbar.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar.set)
frame_operaciones = tk.Frame(canvas, bg=COLOR_FONDO)
canvas.create_window((0, 0), window=frame_operaciones, anchor="nw")
frame_operaciones.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))# Función para seleccionar el archivo

# Función para seleccionar el archivo JSON
def seleccionar_archivo():
    global RUTA_JSON, HASH_ARCHIVO_ACTUAL
    archivo_seleccionado = filedialog.askopenfilename(
        title="Seleccionar salida",
        filetypes=[("Archivos JSON", "*.json")],
        initialdir="future/estrategias/infinity/salida"
    )
    if archivo_seleccionado:
        RUTA_JSON = archivo_seleccionado
        HASH_ARCHIVO_ACTUAL = None  # Reinicia el hash para detectar cambios
        data = cargar_json()
        if data:
            actualizar_interfaz(data)

# Función para cargar el archivo JSON y actualizar la interfaz
def cargar_json():
    try:
        with open(RUTA_JSON, "r") as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        print("Archivo JSON no encontrado.")
        return None
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")
        return None

# Función para actualizar los datos en la interfaz
def actualizar_interfaz(data):
    # Borrar contenido previo
    for widget in frame_operaciones.winfo_children():
        widget.destroy()

    # Actualizar el encabezado con información general
    redondear = 8 if data.get('inverso', False) else 2
    for widget in frame_principal.winfo_children():
        widget.destroy()

    titulo_label = tk.Label(frame_principal, text=f"- INFINITY FUTURE {'INVERSO' if data.get('inverso', False) else 'LINEAL'} - {data.get('activo', '')} - {datetime.fromtimestamp(int(data.get('fecha_inicio', 0))/1000).strftime('%d-%m-%Y %I:%M:%S %p')} -", font=("Arial", 10, "bold"), bg=COLOR_FONDO, fg=COLOR_TITULO, anchor="w")
    titulo_label.pack(fill="none", padx=10, pady=5)

    info_general = [
        f"Balance inicial: {round(float(data['balance_inicial']), redondear)} {'USDT' if not data['inverso'] else data['activo']}",
        f"Balance actual: {round(float(data['balance_actual']), redondear)} {'USDT' if not data['inverso'] else data['activo']}",
        f"Ganancias del grid: {round(float(data['ganancias_del_grid']), redondear)} {'USDT' if not data['inverso'] else data['activo']} ({round(100*float(data['ganancias_del_grid'])/float(data['balance_inicial']), 2)}%)   ({data['parejas_completadas']}/{data['cantidad_parejeas']})",
        f"Ganancia actual: {round(float(data['balance_actual'])-float(data['balance_inicial']), redondear)} {'USDT' if not data['inverso'] else data['activo']} ({round(float(data['ganancia_actual']), 2)}%)   ({round(float(data['beneficio_maximo']), 2)}% / {round(float(data['riesgo_maximo']), 2)}%)"
    ]

    for info in info_general:
        label_info = tk.Label(frame_principal, text=info, font=("Arial", 10), bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w")
        label_info.pack(fill="x", padx=10, pady=2)

    # Agregar operaciones al canvas
    for datos in data['parejas']:
        ganancia = float(datos['general']['beneficios'])
        ganancia_color = COLOR_POSITIVO if ganancia >= 0 else COLOR_NEGATIVO
        info_grid = f"{datos['general']['fecha']}   ---   +{round(ganancia, 8)} {data['activo'] if data['inverso'] else 'USDT'}"

        datos_compra = [
            f"Precio: {datos['compra']['price']}",
            f"Cantidad: {datos['compra']['cantidad']} {data['activo']}",
            f"Monto: {round(float(datos['compra']['monto']), 2)} USDT",
            f"Ejecutada: {datos['compra']['fecha_ejecucion']}"
        ]
        datos_venta = [
            f"Precio: {datos['venta']['price']}",
            f"Cantidad: {datos['venta']['cantidad']} {data['activo']}",
            f"Monto: {round(float(datos['venta']['monto']), 2)} USDT",
            f"Ejecutada: {datos['venta']['fecha_ejecucion']}"
        ]

        crear_operacion(frame_operaciones, info_grid, datos_compra, datos_venta, ganancia_color)

# Función para crear un marco para operaciones
def crear_operacion(frame_padre, info_grid, datos_compra, datos_venta, ganancia_color):
    # Frame contenedor de todo el bloque (con borde)
    frame_operacion = tk.Frame(frame_padre, bg=COLOR_SECCION, highlightbackground=COLOR_BORDE, highlightthickness=2)
    frame_operacion.pack(fill="x", pady=5, padx=10)

    # Fecha y ganancia del grid
    grid_label = tk.Label(frame_operacion, text=info_grid, font=("Arial", 10, "bold"), bg=COLOR_SECCION, fg=ganancia_color, anchor="w")
    grid_label.pack(fill="x", padx=10, pady=5)

    # Frame interno para las dos columnas
    frame_fila = tk.Frame(frame_operacion, bg=COLOR_SECCION)
    frame_fila.pack(fill="x", pady=5)

    # Frame para las operaciones de compra
    frame_compra = tk.Frame(frame_fila, bg=COLOR_SECCION)
    frame_compra.pack(side="left", fill="both", expand=True, padx=(10, 5))

    # Frame para las operaciones de venta
    frame_venta = tk.Frame(frame_fila, bg=COLOR_SECCION)
    frame_venta.pack(side="left", fill="both", expand=True, padx=(5, 10))

    # Etiquetas para los datos de compra
    label_compra = tk.Label(frame_compra, text="Compra", font=("Arial", 10, "bold"), bg=COLOR_SECCION, fg="green", anchor="w", justify="left")
    label_compra.pack(fill="x", padx=5, pady=2)
    for dato in datos_compra:
        label_dato_compra = tk.Label(frame_compra, text=dato, font=("Arial", 9), bg=COLOR_SECCION, fg=COLOR_TEXTO, anchor="w", justify="left")
        label_dato_compra.pack(fill="x", padx=5, pady=2)

    # Etiquetas para los datos de venta
    label_venta = tk.Label(frame_venta, text="Venta", font=("Arial", 10, "bold"), bg=COLOR_SECCION, fg="red", anchor="w", justify="left")
    label_venta.pack(fill="x", padx=5, pady=2)
    for dato in datos_venta:
        label_dato_venta = tk.Label(frame_venta, text=dato, font=("Arial", 9), bg=COLOR_SECCION, fg=COLOR_TEXTO, anchor="w", justify="left")
        label_dato_venta.pack(fill="x", padx=5, pady=2)

# Función que verifica cambios en el archivo JSON
def monitorizar_cambios():
    global HASH_ARCHIVO_ACTUAL
    while True:
        # Calcular hash del archivo actual
        try:
            nuevo_hash = os.stat(RUTA_JSON).st_mtime
        except FileNotFoundError:
            nuevo_hash = None

        # Si el hash ha cambiado, recargar datos
        if nuevo_hash != HASH_ARCHIVO_ACTUAL:
            HASH_ARCHIVO_ACTUAL = nuevo_hash
            data = cargar_json()
            if data:
                root.after(0, lambda: actualizar_interfaz(data))
        time.sleep(0.54)  # Intervalo de actualización (en segundos)

# Iniciar el monitoreo en un hilo separado
hilo_monitor = threading.Thread(target=monitorizar_cambios, daemon=True)
hilo_monitor.start()

# Cargar datos iniciales
'''
if RUTA_JSON == "" or not RUTA_JSON:
    seleccionar_archivo()
'''
data_inicial = cargar_json()
if data_inicial:
    actualizar_interfaz(data_inicial)

# Botón para seleccionar archivo
boton_seleccionar_archivo = tk.Button(
    root,
    text="Seleccionar Archivo",
    command=seleccionar_archivo,
    bg=COLOR_TEXTO,
    fg=COLOR_FONDO
)
boton_seleccionar_archivo.pack(pady=5)

root.mainloop()
