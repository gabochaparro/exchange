import tkinter as tk

# Crear ventana principal
root = tk.Tk()
root.title("Selector de opciones - Tkinter")
root.geometry("300x200")

# Variable para almacenar la opción seleccionada
opcion_seleccionada = tk.StringVar(value="local")  # Inicializa sin selección

# Etiqueta de la pregunta
pregunta = tk.Label(root, text="¿Cuál es la capital de Francia?", font=("Arial", 12))
pregunta.pack(pady=10)

# Opciones como botones de radio
opciones = [("Local", "local"), ("Servidor", "remoto")]

for texto, valor in opciones:
    boton = tk.Radiobutton(
        root,
        text=texto,               # Texto mostrado
        value=valor,              # Valor asociado a la opción
        variable=opcion_seleccionada,  # Vincula la selección a la variable
        font=("Arial", 10),
        indicatoron=True  # Muestra el indicador circular
    )
    boton.pack(anchor="w", padx=20)

# Botón para mostrar la opción seleccionada
def mostrar_seleccion():
    seleccion = opcion_seleccionada.get()

boton_mostrar = tk.Button(root, text="Mostrar selección", command=mostrar_seleccion)
boton_mostrar.pack(pady=10)

# Iniciar el bucle de la aplicación
root.mainloop()
