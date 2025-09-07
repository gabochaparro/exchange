import tkinter as tk
from tkinter import ttk


class TemporizadorTk(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Temporizador con Tkinter")
        self.geometry("350x200")

        # Entrada de tiempo
        self.label_entrada = tk.Label(self, text="Introduce el tiempo en segundos")
        self.label_entrada.pack(pady=5)
        self.input_segundos = tk.Entry(self)
        self.input_segundos.pack(pady=5)

        # Botón para iniciar
        self.boton_iniciar = tk.Button(self, text="Iniciar temporizador", command=self.iniciar_temporizador)
        self.boton_iniciar.pack(pady=5)

        # Label para mostrar el tiempo
        self.label_tiempo = tk.Label(self, text="Tiempo restante: 0", font=("Arial", 14, "bold"))
        self.label_tiempo.pack(pady=5)

        # Barra de progreso
        self.progreso = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progreso.pack(fill="x", padx=20, pady=10)

        # Variables internas
        self.tiempo_total = 0
        self.tiempo_restante = 0

    def iniciar_temporizador(self):
        try:
            self.tiempo_total = int(self.input_segundos.get())
            self.tiempo_restante = self.tiempo_total

            if self.tiempo_total > 0:
                self.label_tiempo.config(text=f"Tiempo restante: {self.tiempo_restante}")
                self.progreso["maximum"] = self.tiempo_total
                self.progreso["value"] = 0  # empieza vacía
                self.after(1000, self.actualizar_tiempo)
            else:
                self.label_tiempo.config(text="Introduce un número mayor a 0")
        except ValueError:
            self.label_tiempo.config(text="Por favor ingresa un número válido")

    def actualizar_tiempo(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.label_tiempo.config(text=f"Tiempo restante: {self.tiempo_restante}")

            progreso_actual = self.tiempo_total - self.tiempo_restante
            self.progreso["value"] = progreso_actual

            # Llamar de nuevo en 1000ms (1 seg)
            self.after(1000, self.actualizar_tiempo)
        else:
            self.label_tiempo.config(text="¡Tiempo finalizado!")
            self.progreso["value"] = self.tiempo_total


if __name__ == "__main__":
    app = TemporizadorTk()
    app.mainloop()
