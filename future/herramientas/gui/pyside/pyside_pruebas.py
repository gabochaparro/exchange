import sys
from PySide6 import QtWidgets, QtCore

# Crear la aplicación
app = QtWidgets.QApplication(sys.argv)

# Crear ventana
ventana = QtWidgets.QWidget()
ventana.setWindowTitle("Tres columnas con texto y botón")

# Layout vertical para una sola columna
layout_verical = QtWidgets.QVBoxLayout()

# Texto
texto = QtWidgets.QLabel(f"Hola PySide6!")
texto.setStyleSheet("font-size: 16px;")
texto.setAlignment(QtCore.Qt.AlignCenter)

# Botón
boton = QtWidgets.QPushButton("Haz clic aquí")
boton.setStyleSheet("font-size: 14px; padding: 6px;")

# Conectar acción del botón
def boton_presionado():
    texto.setText("Botón Presionado")

boton.clicked.connect(boton_presionado)

# Agregar al layout vertical (el orden importa)
layout_verical.addWidget(texto)
layout_verical.addWidget(boton)

# Asignar layout principal a la ventana
ventana.setLayout(layout_verical)

# Mostrar ventana
ventana.show()

# Iniciar loop de eventos
sys.exit(app.exec())
