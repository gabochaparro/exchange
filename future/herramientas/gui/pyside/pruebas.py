import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QProgressBar
)
from PySide6.QtCore import QTimer


class Temporizador(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Temporizador con PySide6")
        self.resize(350, 200)

        # Layout principal
        layout = QVBoxLayout()

        # Entrada de tiempo en segundos
        self.input_segundos = QLineEdit()
        self.input_segundos.setPlaceholderText("Introduce segundos")
        layout.addWidget(self.input_segundos)

        # Botón para iniciar
        self.boton_iniciar = QPushButton("Iniciar temporizador")
        self.boton_iniciar.clicked.connect(self.iniciar_temporizador)
        layout.addWidget(self.boton_iniciar)

        # Label para mostrar cuenta regresiva
        self.label_tiempo = QLabel("Tiempo restante: 0")
        self.label_tiempo.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(self.label_tiempo)

        # Barra de progreso
        self.progreso = QProgressBar()
        self.progreso.setMinimum(0)
        self.progreso.setValue(0)  # comienza vacía
        layout.addWidget(self.progreso)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_tiempo)

        self.tiempo_restante = 0
        self.tiempo_total = 0

        self.setLayout(layout)

    def iniciar_temporizador(self):
        try:
            self.tiempo_total = int(self.input_segundos.text())
            self.tiempo_restante = self.tiempo_total

            if self.tiempo_total > 0:
                self.label_tiempo.setText(f"Tiempo restante: {self.tiempo_restante}")
                self.progreso.setMaximum(self.tiempo_total)
                self.progreso.setValue(0)  # inicia vacía
                self.timer.start(1000)  # cada 1 segundo
            else:
                self.label_tiempo.setText("Introduce un número mayor a 0")
        except ValueError:
            self.label_tiempo.setText("Por favor ingresa un número válido")

    def actualizar_tiempo(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.label_tiempo.setText(f"Tiempo restante: {self.tiempo_restante}")

            # Progreso calculado (llenándose)
            progreso_actual = self.tiempo_total - self.tiempo_restante
            self.progreso.setValue(progreso_actual)
        else:
            self.timer.stop()
            self.label_tiempo.setText("¡Tiempo finalizado!")
            self.progreso.setValue(self.tiempo_total)  # llena al final


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Temporizador()
    ventana.show()
    sys.exit(app.exec())
