import sys
from PySide6 import QtWidgets

# Crear aplicación
app = QtWidgets.QApplication(sys.argv)

# Crear ventana
ventana = QtWidgets.QWidget()
ventana.setWindowTitle("Ventana de PySide6")
ventana.resize(400,200)

# Crear el layout principal y los secundarios
layout_principal = QtWidgets.QHBoxLayout()
layout_1 = QtWidgets.QVBoxLayout()
layout_2 = QtWidgets.QVBoxLayout()

# Agregar los layouts secundarios al principal
layout_principal.addLayout(layout_1)
layout_principal.addLayout(layout_2)

# Insertar el layout en la ventana
ventana.setLayout(layout_principal)

# Crear una etiqueta
etiqueta = QtWidgets.QLabel("Etiqueta de PySide6")

# Crear una entrada
entrada = QtWidgets.QLineEdit(placeholderText="Introduce el número de proceo")

# Función para el botón
def correr_proceso():
    proceso = entrada.text()
    etiqueta.setText(f"Corriendo proceso {proceso} . . .")

# Crear un botón
boton = QtWidgets.QPushButton("Correr")
boton.clicked.connect(correr_proceso)

# Agregar los widgets al layout correspondiente
layout_1.addWidget(entrada)
layout_1.addWidget(boton)
layout_2.addWidget(etiqueta)

# Mostrar la ventana
ventana.show()

# Correr el ciclo hasta que se cierre la ventana
sys.exit(app.exec())