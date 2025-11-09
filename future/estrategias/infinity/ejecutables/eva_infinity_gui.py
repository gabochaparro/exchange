import tkinter as tk
import json
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
from datetime import datetime
import glob
import subprocess
import platform
import datos_servidor
import sys

try:
    # Directorios locales
    directorio_credenciales = os.path.dirname(sys.executable) + "/future/estrategias/infinity/credenciales.json"
    parametros_iniciales = os.path.dirname(sys.executable) + "/future/estrategias/infinity/parametros_infinity_2.0.json"
    carpeta_parametros = os.path.dirname(sys.executable) + "/future/estrategias/infinity/parametros/*"
    carpeta_salida = os.path.dirname(sys.executable) + "/future/estrategias/infinity/salida/*"
    ruta_infinity = os.path.dirname(sys.executable) + "/infinity_20"
    ruta_infinity_servidor = os.path.dirname(sys.executable) + "/infinity_20_remoto"

    # Directorios remotos
    CREDENCIALES_REMOTO = "/home/ubuntu/exchange/future/estrategias/infinity" # Directorio en EC2 donde están las credenciales
    PARAMETROS_REMOTO = "/home/ubuntu/exchange/future/estrategias/infinity"  # Directorio en EC2 donde están los parametros iniciales
    PARAMETROS_LIVE_REMOTO = "/home/ubuntu/exchange/future/estrategias/infinity/parametros"  # Directorio en EC2 donde están los parametros en vivo
    SALIDA_REMOTO = "/home/ubuntu/exchange/future/estrategias/infinity/salida" # Directorio en EC2 donde están las salidas

except Exception as e:
    print("ERROR LEYENDO DIRECTORIOS")
    print(e)
    input("PRESIONA ENTER PARA SALIR")

# Colores personalizados
COLOR_FONDO = "#1e1e2f"
COLOR_TEXTO = "#e0e0e0"
COLOR_TITULO = "#ff9900"
COLOR_SECCION = "#29293d"
COLOR_BORDE = "#404056"
COLOR_POSITIVO = "#00ff00"
COLOR_NEGATIVO = "#ff0000"

activo = ""
tipo = ""

# Función para cargar el archivo JSON
def cargar_parametros_json(ruta):
    global data, ruta_archivo, nombre_archivo
    try:
        nombre_archivo = ruta.split("/")[-1]
        ventana.title(f"Eva Infinity 2.0 - {nombre_archivo.split(".json")[0]}")
        
        # Borrar contenido previo
        for widget in header_top.winfo_children():
            widget.destroy()
        header_label = ttk.Label(header_top, text=f"- INFINITY FUTURE - {nombre_archivo.split(".json")[0]} - {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')} -", style="Header.TLabel")
        header_label.pack(anchor="center")
        
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
        ruta_archivo = ruta
        actualizar_parametros()
    except Exception as e:
        print("Error", f"No se pudo cargar lo parametros: {e}")

# Función que actualiza la interfaz
def actualizar_parametros():
    for widget in frame_editor.winfo_children():
        widget.destroy()  # Limpiar el frame antes de cargar nuevos valores
    entries.clear()
    botones_booleanos.clear()

    if "inverso" in data:
        if data['inverso']:
            base_coin = data['activo'].upper()
        else:
            base_coin = "USDT"

    for i, (clave, valor) in enumerate(data.items()):

        # Mostrar clave como texto no editable
        tk.Label(frame_editor, text=f"{clave}:", anchor="w", width=22).grid(row=i + 2, column=0, padx=1.8, pady=1.8)

        if isinstance(valor, bool):  # Crear un botón toggle para valores booleanos
            if clave == 'pausa':
                if valor:
                    btn_toggle = tk.Button(frame_editor, text="Sí" if valor else "No", width=6, fg="black", bg="red", 
                                            command=lambda c=clave: toggle_boolean(c))
                else:
                    btn_toggle = tk.Button(frame_editor, text="Sí" if valor else "No", width=6, fg="black", bg="green",
                                            command=lambda c=clave: toggle_boolean(c))
            else:
                btn_toggle = tk.Button(frame_editor, text="Sí" if valor else "No", width=6, 
                                        command=lambda c=clave: toggle_boolean(c))
            btn_toggle.grid(row=i + 2, column=1, padx=1.8, pady=1.8)
            botones_booleanos[clave] = btn_toggle

        elif clave == 'direccion':  # Usar OptionMenu para LONG, RANGO, SHORT
            opciones = ["LONG", "RANGO", "SHORT"]
            valor_actual = "RANGO" if valor == "" else str(valor).upper()
            seleccion = tk.StringVar(value=valor_actual)

            def actualizar_direccion(*args, clave=clave):
                data[clave] = "" if seleccion.get() == "RANGO" else seleccion.get()
                # Cambiar color según la dirección seleccionada
                color = "green" if seleccion.get() == "LONG" else "yellow" if seleccion.get() == "RANGO" else "red"
                menu.config(bg=color)

            seleccion.trace("w", actualizar_direccion)
            menu = tk.OptionMenu(frame_editor, seleccion, *opciones)
            menu.config(width=5, fg="black", bg="green" if valor_actual == "LONG" else "yellow" if valor_actual == "RANGO" else "red")
            menu.grid(row=i + 2, column=1, padx=0.9, pady=0.9)

        elif clave == 'exchange':  # Usar OptionMenu para BYBIT y BINANCE
            if nombre_archivo == "parametros_infinity_2.0.json":
                opciones_exchange = ["BYBIT", "BINANCE"]
                seleccion_exchange = tk.StringVar(value=str(valor).upper())

                def actualizar_exchange(*args, clave=clave):
                    data[clave] = seleccion_exchange.get()

                seleccion_exchange.trace("w", actualizar_exchange)
                menu_exchange = tk.OptionMenu(frame_editor, seleccion_exchange, *opciones_exchange)
                menu_exchange.config(width=5)
                menu_exchange.grid(row=i + 2, column=1, padx=1.8, pady=1.8)
            else:
                label_valor = tk.Label(frame_editor, text=str(valor).upper(), anchor="w", width=9)
                label_valor.grid(row=i + 2, column=1, padx=1.8, pady=1.8)

        elif clave == 'activo':  # Campo editable solo si es el archivo permitido
            if nombre_archivo == "parametros_infinity_2.0.json":
                entry = tk.Entry(frame_editor, width=9)
                entry.insert(0, str(valor).upper())
                entry.grid(row=i + 2, column=1, padx=1.8, pady=1.8)
                entries[clave] = entry
            else:
                label_valor = tk.Label(frame_editor, text=str(valor).upper(), anchor="w", width=9)
                label_valor.grid(row=i + 2, column=1, padx=1.8, pady=1.8)
        
        else:  # Otros tipos (int, float, etc.) como campos editables
            if 'beneficio_max' != clave != 'riesgo_max':
                entry = tk.Entry(frame_editor, width=9)
                entry.insert(0, str(valor))
                entry.grid(row=i + 2, column=1, padx=1.8, pady=1.8)
                entries[clave] = entry

# Función para alternar valores booleanos
def toggle_boolean(clave):
    if clave != "inverso" or nombre_archivo == "parametros_infinity_2.0.json":
        valor_actual = data[clave]
        data[clave] = not valor_actual  # Alternar entre True y False
        btn_toggle = botones_booleanos[clave]
        btn_toggle.config(text="Sí" if data[clave] else "No")

# Función para guardar cambios en el archivo JSON
def guardar_parametros_json():
    global activo, tipo
    try:
        for clave, entry in entries.items():
            valor = entry.get()
            try:
                data[clave] = eval(valor)  # Convertir al tipo adecuado
            except:
                data[clave] = valor  # Mantener como string si falla la conversión

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        activo = data['activo'].upper()
        tipo = "INVERSO" if data['inverso'] else "LINEAL"

        if opcion_seleccionada.get() == "remoto":
            if ruta_archivo == parametros_iniciales:
                ruta_remota = PARAMETROS_REMOTO
            else:
                ruta_remota = PARAMETROS_LIVE_REMOTO
            ok = datos_servidor.subir_archivo_remoto(ruta_remota,ruta_archivo.split(os.path.basename(ruta_archivo))[0],os.path.basename(ruta_archivo))

            if ok == "OK":
                messagebox.showinfo("Exito", "Parametros enviados al servidor correctamente")
            else:
                messagebox.showerror("Error", "Parametros no enviados")
        else:
            messagebox.showinfo("Exito", "Parametros enviados correctamente")

    except Exception as e:
        print("Error", f"No se pudo guardar el archivo: {e}")
        messagebox.showerror("ERROR", "Error guardando parametros")

# Función para monitorear cambios en el archivo JSON
def monitorear_cambios_parametros():
    global activo, tipo
    ultimo = float(os.path.getmtime(parametros_iniciales))
    ultimo_modificado = {}
    while True:
        try:
            # Obtener los archivos de la carpeta parametros
            archivo_parametros = glob.glob(carpeta_parametros)

            # Buscar el archivo con la ultima modificacion
            for archivo in archivo_parametros:
                if float(os.path.getmtime(archivo)) > ultimo and json.load(open(archivo,"r")) != ultimo_modificado:
                    ultimo = float(os.path.getmtime(archivo))
                    ultimo_modificado = json.load(open(archivo,"r"))
                    if activo in archivo and tipo in archivo:
                        cargar_parametros_json(archivo)

        except Exception as e:
            print(f"Error monitoreando el archivo: {e}")
        time.sleep(1)  # Verificar cada segundo

# Función para cargar el archivo JSON y actualizar la interfaz
def cargar_json_salida():
    try:
        # Usa glob para obtener todos los archivos dentro de la carpeta
        archivos_salida = glob.glob(carpeta_salida)
            
        # Esperar hasta que se generen los archivos de salida
        while len(archivos_salida) == 0:
            archivos_salida = glob.glob(carpeta_salida)

        # Ubicar la ruta long y short
        ruta_salida_long = {}
        for archivo in archivos_salida:
            if "LONG" in archivo and activo in archivo and tipo in archivo:
                ruta_salida_long = archivo
        
                with open(ruta_salida_long, "r") as archivo:
                    salida_long = json.load(archivo)
                    return salida_long
    
    except FileNotFoundError:
        print("Archivo JSON no encontrado.")
        return None
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")
        return None

# Función para cargar el archivo JSON y actualizar la interfaz
def cargar_json_salida_short():
    try:
        # Usa glob para obtener todos los archivos dentro de la carpeta
        archivos_salida = glob.glob(carpeta_salida)
        
        # Esperar hasta que se generen los archivos de salida
        while len(archivos_salida) == 0:
            archivos_salida = glob.glob(carpeta_salida)

        # Ubicar la ruta long y short
        ruta_salida_short = {}
        for archivo in archivos_salida:
            if "SHORT" in archivo and activo in archivo and tipo in archivo:
                ruta_salida_short = archivo
        
                with open(ruta_salida_short, "r") as archivo:
                    salida_short = json.load(archivo)
                    return salida_short
    
    except FileNotFoundError:
        print("Archivo JSON no encontrado.")
        return None
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON.")
        return None

def crear_interfaz():
    global frame_editor, entries, botones_booleanos, ventana, data, frame_editor_id, ruta_archivo, ultima_modificacion, frame_izquierdo, nombre_archivo, header_left, header_top, opcion_seleccionada
    # Crear la ventana principal
    ventana = tk.Tk()
    nombre_archivo = "Eva Future Infinity"
    ventana.title(f"{nombre_archivo}")
    ventana.geometry("1200x800")  # Ancho x Alto
    
    # Estilo general
    estilo = ttk.Style()
    estilo.configure("TFrame", background="#1e1e2e")
    estilo.configure("Header.TLabel", background="#1e1e2e", foreground=COLOR_TITULO, font=("Arial", 12, "bold"))
    estilo.configure("Content.TLabel", background="#1e1e2e", foreground="#ffffff", font=("Arial", 10))
    estilo.configure("Custom.TFrame", borderwidth=6, relief="solid", background="black")

    # Frame del header
    header = ttk.Frame(ventana, height=80, relief="raised")
    header.pack(side="top", fill="x")

    # Subframes dentro del header
    header_top = ttk.Frame(header, relief="flat")
    header_top.pack(side="top", fill="x", padx=10, pady=10)
    
    header_left = ttk.Frame(header, width=200, relief="flat")
    header_left.pack(side="left", fill="x", padx=10, pady=3)
    
    header_center = ttk.Frame(header, width=200, relief="flat")
    header_center.pack(side="left", fill="x", padx=10, pady=3, expand=True)

    header_right = ttk.Frame(header, width=200, relief="flat")
    header_right.pack(side="right", fill="x", padx=10)

    # Información del balance en el header izquierdo
    balance_inicial = ttk.Label(header_left, text="Balance inicial: - USDT", style="Content.TLabel")
    balance_inicial.pack(anchor="w", pady=2)

    balance_actual = ttk.Label(header_left, text="Balance actual: - USDT", style="Content.TLabel")
    balance_actual.pack(anchor="w", pady=2)

    ganancia_actual = ttk.Label(header_left, text="Ganancia actual: - USDT (0%) (0% / 0%)", style="Content.TLabel")
    ganancia_actual.pack(anchor="w", pady=2)

    # Título principal en el header top
    header_label = ttk.Label(header_top, text=f"- INFINITY FUTURE - {nombre_archivo.split(".json")[0]} -", style="Header.TLabel")
    header_label.pack(anchor="center")

    # Botón para correr el infinity 2.0 en el header central
    header_radiobutton = ttk.Frame(header_center, width=200, relief="flat")
    header_radiobutton.pack(padx=10, pady=3)
    
    # Variable para almacenar la opción seleccionada
    opcion_seleccionada = tk.StringVar(value="local")  # Inicializa sin selección

    # Opciones como botones de radio
    opciones = [("Local", "local"), ("Servidor", "remoto")]
    i=0
    for texto, valor in opciones:
        boton = tk.Radiobutton(
            header_radiobutton,
            text=texto,               # Texto mostrado
            value=valor,              # Valor asociado a la opción
            variable=opcion_seleccionada,  # Vincula la selección a la variable
            font=("Arial", 10),
            indicatoron=True  # Muestra el indicador circular
        )
        boton.grid(row=0, column=i)
        i=i+1

    # FUNCION PARA CORRER INFINITY 2.0
    def correr_infinity():
        try:
            # Guardar parametros antes de correr el infinity
            guardar_parametros_json()
            
            # Obtener las salidas iniciales del servidor
            if opcion_seleccionada.get() == "remoto":
                ok = ""
                while ok != "OK":
                    # Obtener las salidas iniciales del servidor
                    salidas = datos_servidor.listar_archivos_remotos(SALIDA_REMOTO)
                    for salida in salidas:
                        if "LONG" in salida:
                            ok = datos_servidor.descargar_archivo_remoto(SALIDA_REMOTO,carpeta_salida.split("/*")[0],salida)
                        if ok == "OK":
                            salida_inicial = json.load(open(f"{carpeta_salida.split("/*")[0]}/{salida}","r"))
                            print("SALIDA INICIAL")
                            print(json.dumps(salida_inicial,indent=2))
                            salida_actual = salida_inicial
                            break
            
            # Correr infinity segun el sistema operativo
            if platform.system() == "Windows":
                if opcion_seleccionada.get() == "local":
                    os.startfile(ruta_infinity)
                else:
                    os.startfile(ruta_infinity_servidor)
            
            elif platform.system() == "Darwin":  # macOS
                if opcion_seleccionada.get() == "local":
                    subprocess.run(["open", ruta_infinity])
                else:
                    subprocess.run(["open", ruta_infinity_servidor])
            
            else:  # Linux
                if opcion_seleccionada.get() == "local":
                    subprocess.run(["xdg-open", ruta_infinity])
                else:
                    subprocess.run(["xdg-open", ruta_infinity_servidor])

            # Iniciar los hilos que extraen los archivos del servidor en modo remoto
            if opcion_seleccionada.get() == "remoto":
                while salida_inicial == salida_actual:
                    ok = ""
                    while ok != "OK":
                        # Obtener las salidas iniciales del servidor
                        salidas = datos_servidor.listar_archivos_remotos(SALIDA_REMOTO)
                        for salida in salidas:
                            if "LONG" in salida:
                                ok = datos_servidor.descargar_archivo_remoto(SALIDA_REMOTO,carpeta_salida.split("/*")[0],salida)
                            if ok == "OK":
                                salida_actual = json.load(open(f"{carpeta_salida.split("/*")[0]}/{salida}","r"))
                                print("SALIDA ACTUAL")
                                print(json.dumps(salida_actual,indent=2))
                                break
                threading.Thread(target=datos_servidor.parametros_actualizados, daemon=True).start()
                threading.Thread(target=datos_servidor.salidas_actualizadas, daemon=True).start()
            
            cargar_json_salida()
            cargar_json_salida_short()

        except Exception as e:
            print("ERROR CORRIENDO EL EJECUTABLE INFINITY")
            print(e)
            print("")
    
    boton_infinity = ttk.Button(header_center, text=f"CORRER INFINITY 2.0", command=correr_infinity)
    boton_infinity.pack()

    # Entradas para API Key y API Secret en el header derecho
    try:
        credenciales = json.load(open(directorio_credenciales, "r"))
    except Exception as e:
        print("ERROR CARGANDO CREDENCIALES")
        print(e)
        print("")
    
    api_key_label = ttk.Label(header_right, text="API Key:", style="Content.TLabel")
    api_key_label.grid(row=0, column=0, padx=5, pady=2, sticky="e")

    api_key_entry = ttk.Entry(header_right, width=30)
    api_key_entry.grid(row=0, column=1, padx=5, pady=2)
    api_key_entry.insert(0,credenciales['api_key'])

    api_secret_label = ttk.Label(header_right, text="API Secret:", style="Content.TLabel")
    api_secret_label.grid(row=1, column=0, padx=5, pady=2, sticky="e")

    api_secret_entry = ttk.Entry(header_right, width=30, show="*")
    api_secret_entry.grid(row=1, column=1, padx=5, pady=2)
    api_secret_entry.insert(0,credenciales['api_secret'])

    # Funcion para guardar credenciales
    def guardar_credenciales():
        try:
            credenciales = json.load(open(directorio_credenciales, "r"))
            credenciales['api_key'] = api_key_entry.get()
            credenciales['api_secret'] = api_secret_entry.get()
            json.dump(credenciales, open(directorio_credenciales, "w"), indent=4)
            if opcion_seleccionada.get() == "remoto":
                datos_servidor.subir_archivo_remoto(CREDENCIALES_REMOTO,directorio_credenciales.split("credenciales.json")[0],"credenciales.json")
            messagebox.showinfo("Guardado exitoso", "Credenciales guardadas correctamente.")
        except Exception as e:
            print("ERROR GUARDANDO CREDENCIALES")
            print(e)
            print("")
            messagebox.showinfo("Error", "ERROR GUARDANDO CREDENCIALES")

    guardar_button = ttk.Button(header_right, text="Guardar Credenciales", command=guardar_credenciales)
    guardar_button.grid(row=0, column=2, rowspan=2)

    # Frame del cuerpo central
    cuerpo = ttk.Frame(ventana)
    cuerpo.pack(expand=True, fill="both")

    # Tres frames verticales en el centro
    frame_izquierdo = ttk.Frame(cuerpo, width=200, relief="sunken")
    frame_izquierdo.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    frame_central = ttk.Frame(cuerpo, width=200, relief="sunken")
    frame_central.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    frame_derecho = ttk.Frame(cuerpo, width=200, relief="sunken")
    frame_derecho.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    # Frame del footer
    footer = ttk.Frame(ventana, height=30, relief="raised")
    footer.pack(side="bottom", fill="x")

    # Etiqueta en el footer
    footer_label = ttk.Label(footer, text="Footer - Información Adicional", anchor="center")
    footer_label.pack(expand=True)

    
    # -------------PARAMETROS-------------------
    # Boton de enviar parametros
    boton_guardar = tk.Button(frame_izquierdo, text="Enviar", command=guardar_parametros_json)
    boton_guardar.pack(pady=5)

    # Contenedor con Canvas para agregar scroll
    canvas = tk.Canvas(frame_izquierdo)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(frame_izquierdo, orient="vertical", command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame dentro del Canvas
    frame_editor = tk.Frame(canvas)
    frame_editor_id = canvas.create_window((0, 0), window=frame_editor, anchor="nw")

    # Función para ajustar el scroll al contenido
    def ajustar_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))

    frame_editor.bind("<Configure>", ajustar_scroll)

    # Permitir desplazamiento con la rueda del mouse
    def scroll_mouse(event):
        if event.num == 4 or event.delta > 0:  # Scroll up
            canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:  # Scroll down
            canvas.yview_scroll(1, "units")

    # Vincular eventos según la plataforma
    if ventana.tk.call("tk", "windowingsystem") == "aqua":  # macOS
        canvas.bind_all("<Button-4>", scroll_mouse)
        canvas.bind_all("<Button-5>", scroll_mouse)
    else:  # Windows y Linux
        canvas.bind_all("<MouseWheel>", scroll_mouse)

    # Variables globales
    data = {}
    ultima_modificacion = None
    entries = {}  # Para campos editables no booleanos
    botones_booleanos = {}  # Para botones toggle
    ruta_archivo = None  # Para carga y descarga remota
    
    # Cargar y gurdar los parametros iniciales
    cargar_parametros_json(parametros_iniciales)
    guardar_parametros_json()

    # Iniciar el monitoreo en un hilo aparte
    hilo_monitoreo = threading.Thread(target=monitorear_cambios_parametros, daemon=True)
    hilo_monitoreo.start()
    # -------------FIN PARAMETROS-------------------
    
    # -------------SALIDA LONG-------------------
    # Frame principal para información general
    frame_principal = tk.Frame(frame_central, bg=COLOR_FONDO)
    frame_principal.pack(side="top", fill="x", padx=10, pady=5)

    # Canvas para las operaciones
    frame_con_canvas = tk.Frame(frame_central, bg=COLOR_FONDO)
    frame_con_canvas.pack(side="top", fill="both", expand=True)
    canvas = tk.Canvas(frame_con_canvas, bg=COLOR_FONDO, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(frame_con_canvas, orient="vertical", command=canvas.yview, bg=COLOR_FONDO)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    frame_operaciones = tk.Frame(canvas, bg=COLOR_FONDO)
    canvas.create_window((0, 0), window=frame_operaciones, anchor="nw")
    frame_operaciones.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))# Función para seleccionar el archivo

    # Función para actualizar los datos en la interfaz
    def actualizar_interfaz_long(data):
        # Borrar contenido previo
        for widget in frame_operaciones.winfo_children():
            widget.destroy()

        # Actualizar el encabezado con información general
        redondear = 8 if data.get('inverso', True) else 2
        for widget in frame_principal.winfo_children():
            widget.destroy()

        titulo_label = tk.Label(frame_principal, text=f"- {data['activo']} GRID LONG -", font=("Arial", 10, "bold"), bg=COLOR_FONDO, fg=COLOR_TITULO, anchor="w")
        titulo_label.pack(fill="none", padx=10, pady=5)
        label_info = tk.Label(frame_principal, text=f"Ganancias del grid: {round(float(data['ganancias_del_grid']), redondear)} {'USDT' if not data['inverso'] else data['activo']} ({round(100*float(data['ganancias_del_grid'])/float(data['balance_inicial']), 2)}%)   ({data['parejas_completadas']}/{data['cantidad_parejeas']})", font=("Arial", 10), bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w")
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
        salida_actual = {}
        while True:
            try:
                # obtener la nueva salida
                nueva_salida = cargar_json_salida()

                # Si la salida ha cambiado cargarla y actualizar
                if nueva_salida != salida_actual:
                    salida_actual = nueva_salida
                    
                    # Borrar contenido previo
                    redondear = 8 if nueva_salida['inverso'] else 2
                    for widget in header_left.winfo_children():
                        widget.destroy()

                    info_general = [
                        f"Balance inicial: {round(float(nueva_salida['balance_inicial']), redondear)} {'USDT' if not nueva_salida['inverso'] else nueva_salida['activo']}",
                        f"Balance actual: {round(float(nueva_salida['balance_actual']), redondear)} {'USDT' if not nueva_salida['inverso'] else nueva_salida['activo']}",
                        f"Ganancia actual: {round(float(nueva_salida['balance_actual'])-float(nueva_salida['balance_inicial']), redondear)} {'USDT' if not nueva_salida['inverso'] else nueva_salida['activo']} ({round(float(nueva_salida['ganancia_actual']), 2)}%)   ({round(float(nueva_salida['beneficio_maximo']), 2)}% / {round(float(nueva_salida['riesgo_maximo']), 2)}%)"
                    ]

                    for info in info_general:
                        label_info = ttk.Label(header_left, text=info, style="Content.TLabel")
                        label_info.pack(anchor="w", pady=2)
                    ventana.after(0, lambda: actualizar_interfaz_long(nueva_salida))
            
            except Exception as e:
                print("ERROR MONITOREANDO SALIDAS LONG")
                print(e)
                print("")

    # Iniciar el monitoreo en un hilo separado
    hilo_monitor = threading.Thread(target=monitorizar_cambios, daemon=True)
    hilo_monitor.start()
    # -------------FIN SALIDA LONG---------------
    

    # -------------SALIDA SHORT-------------------
    # Frame principal para información general
    frame_principal_short = tk.Frame(frame_derecho, bg=COLOR_FONDO)
    frame_principal_short.pack(side="top", fill="x", padx=10, pady=5)

    # Canvas para las operaciones
    frame_con_canvas = tk.Frame(frame_derecho, bg=COLOR_FONDO)
    frame_con_canvas.pack(side="top", fill="both", expand=True)
    canvas = tk.Canvas(frame_con_canvas, bg=COLOR_FONDO, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar = tk.Scrollbar(frame_con_canvas, orient="vertical", command=canvas.yview, bg=COLOR_FONDO)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)
    frame_operaciones_short = tk.Frame(canvas, bg=COLOR_FONDO)
    canvas.create_window((0, 0), window=frame_operaciones_short, anchor="nw")
    frame_operaciones_short.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))# Función para seleccionar el archivo

    # Función para actualizar los datos en la interfaz
    def actualizar_interfaz_short(data):
        # Borrar contenido previo
        for widget in frame_operaciones_short.winfo_children():
            widget.destroy()

        # Actualizar el encabezado con información general
        redondear = 8 if data.get('inverso', True) else 2
        for widget in frame_principal_short.winfo_children():
            widget.destroy()

        titulo_label = tk.Label(frame_principal_short, text=f"- {data['activo']} GRID SHORT -", font=("Arial", 10, "bold"), bg=COLOR_FONDO, fg=COLOR_TITULO, anchor="w")
        titulo_label.pack(fill="none", padx=10, pady=5)
        label_info = tk.Label(frame_principal_short, text=f"Ganancias del grid: {round(float(data['ganancias_del_grid']), redondear)} {'USDT' if not data['inverso'] else data['activo']} ({round(100*float(data['ganancias_del_grid'])/float(data['balance_inicial']), 2)}%)   ({data['parejas_completadas']}/{data['cantidad_parejeas']})", font=("Arial", 10), bg=COLOR_FONDO, fg=COLOR_TEXTO, anchor="w")
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

            crear_operacion_short(frame_operaciones_short, info_grid, datos_compra, datos_venta, ganancia_color)

    # Función para crear un marco para operaciones
    def crear_operacion_short(frame_padre, info_grid, datos_compra, datos_venta, ganancia_color):
        # Frame contenedor de todo el bloque (con borde)
        frame_operaciones_short = tk.Frame(frame_padre, bg=COLOR_SECCION, highlightbackground=COLOR_BORDE, highlightthickness=2)
        frame_operaciones_short.pack(fill="x", pady=5, padx=10)

        # Fecha y ganancia del grid
        grid_label = tk.Label(frame_operaciones_short, text=info_grid, font=("Arial", 10, "bold"), bg=COLOR_SECCION, fg=ganancia_color, anchor="w")
        grid_label.pack(fill="x", padx=10, pady=5)

        # Frame interno para las dos columnas
        frame_fila = tk.Frame(frame_operaciones_short, bg=COLOR_SECCION)
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
    def monitorizar_cambios_short():
        salida_actual = {}
        while True:
            try:
                # obtener la nueva salida
                nueva_salida = cargar_json_salida_short()

                # Si la salida ha cambiado cargarla y actualizar
                if nueva_salida != salida_actual:
                    salida_actual = nueva_salida
                    
                    # Borrar contenido previo
                    redondear = 8 if nueva_salida['inverso'] else 2
                    for widget in header_left.winfo_children():
                        widget.destroy()

                    info_general = [
                        f"Balance inicial: {round(float(nueva_salida['balance_inicial']), redondear)} {'USDT' if not nueva_salida['inverso'] else nueva_salida['activo']}",
                        f"Balance actual: {round(float(nueva_salida['balance_actual']), redondear)} {'USDT' if not nueva_salida['inverso'] else nueva_salida['activo']}",
                        f"Ganancia actual: {round(float(nueva_salida['balance_actual'])-float(nueva_salida['balance_inicial']), redondear)} {'USDT' if not nueva_salida['inverso'] else nueva_salida['activo']} ({round(float(nueva_salida['ganancia_actual']), 2)}%)   ({round(float(nueva_salida['beneficio_maximo']), 2)}% / {round(float(nueva_salida['riesgo_maximo']), 2)}%)"
                    ]

                    for info in info_general:
                        label_info = ttk.Label(header_left, text=info, style="Content.TLabel")
                        label_info.pack(anchor="w", pady=2)
                    ventana.after(0, lambda: actualizar_interfaz_short(nueva_salida))
            
            except Exception as e:
                print("ERROR MONITOREANDO SALIDAS SHORT")
                print(e)
                print("")

    # Iniciar el monitoreo en un hilo separado
    hilo_monitor = threading.Thread(target=monitorizar_cambios_short, daemon=True)
    hilo_monitor.start()
    # -------------FIN SALIDA SHORT---------------
    
    # Loop principal de la ventana
    ventana.mainloop()

# Llamar a la función para ejecutar la interfaz
crear_interfaz()
