import os
import subprocess
import sys

try:
    # Ruta al directorio y archivo
    directorio = os.path.dirname(sys.executable)
    archivo = "future/estrategias/infinity/infinity_2.0.py"

    # Cambiar al directorio especificado y ejecutar el archivo
    os.chdir(directorio)
    subprocess.run(["python3", archivo])
except Exception as e:
    print("ERROR CORRIENDO infinity_2.0.py")
    print(e)

input("PRESIONA ENTER PARA SALIR")