import tkinter as tk

# Crear ventana principal
root = tk.Tk()
root.title("Botón con Estilo Mejorado")

# Crear un frame para organizar los widgets
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Botón que ocupa dos filas y tiene un estilo mejorado
boton = tk.Button(
    frame,
    text="Guardar\nCredenciales"  # Texto en dos líneas
)
boton.grid(row=0, column=0, rowspan=2)  # Ocupa dos filas

# Iniciar el bucle principal
root.mainloop()
