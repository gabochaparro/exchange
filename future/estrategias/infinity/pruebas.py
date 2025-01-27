import os
import subprocess
import platform

# Ruta al archivo
ruta_archivo = "/Users/gabochaparro/Desktop/Infinity 20"

def abrir_archivo(ruta_archivo):
    """
    Abre un archivo simulando un doble clic.

    :param ruta_archivo: Ruta completa del archivo a abrir.
    """
    if platform.system() == "Windows":
        os.startfile(ruta_archivo)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", ruta_archivo])
    else:  # Linux
        subprocess.run(["xdg-open", ruta_archivo])

abrir_archivo(ruta_archivo)