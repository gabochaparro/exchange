import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PySide6.QtCore import QProcess

class Ventana(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Terminal embebida con QProcess")
        self.resize(700, 400)

        layout = QVBoxLayout()

        # Área de salida
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        layout.addWidget(self.terminal)

        # Botón para ejecutar un proceso externo
        self.boton = QPushButton("Ejecutar script externo")
        layout.addWidget(self.boton)

        self.setLayout(layout)

        # Proceso de sistema
        self.proceso = QProcess(self)

        # Conectar señales de salida
        self.proceso.readyReadStandardOutput.connect(self.leer_stdout)
        self.proceso.readyReadStandardError.connect(self.leer_stderr)

        # Acción del botón
        self.boton.clicked.connect(self.ejecutar)

    def ejecutar(self):
        """Ejecutar un proceso externo"""
        self.terminal.append("▶ Ejecutando proceso...\n")
        # Ejemplo: comando bash o script Python
        self.proceso.start("python3", ["-u", "/Volumes/Datos/DESARROLLO PERSONAL/PROGRAMAR APLICACIONES WEB/Perfeccionar Python/Proyectos Python/Trading Bot Exchange/exchange/future/herramientas/gui/pyside/prueba.py"])  # -u = salida sin buffer

        # También podrías probar con:
        # self.proceso.start("ls", ["-la"])
        #self.proceso.start("bash", ["-c", "echo Hola && sleep 2 && echo Adiós"])

    def leer_stdout(self):
        """Leer salida estándar"""
        datos = self.proceso.readAllStandardOutput().data().decode()
        self.terminal.insertPlainText(datos)
        self.terminal.ensureCursorVisible()

    def leer_stderr(self):
        """Leer errores estándar"""
        datos = self.proceso.readAllStandardError().data().decode()
        self.terminal.insertPlainText(datos)
        self.terminal.ensureCursorVisible()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec())
