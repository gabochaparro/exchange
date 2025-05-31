import subprocess
import sys
import os

def instalar_requisitos():
    # Determinar la ruta al archivo requirements.txt
    if getattr(sys, 'frozen', False):
        # Si el script está empaquetado con PyInstaller
        ruta_base = os.path.dirname(sys.executable)
    else:
        # Si el script se ejecuta directamente
        ruta_base = os.path.dirname(os.path.abspath(__file__))

    ruta_requisitos = os.path.join(ruta_base, 'requirements.txt')

    if os.path.exists(ruta_requisitos):
        try:
            # Verificar si ya se ha realizado la instalación
            if os.environ.get('REQUIREMENTS_INSTALLED') != '1':
                # Establecer la variable de entorno para evitar la recursión
                os.environ['REQUIREMENTS_INSTALLED'] = '1'
                # Ejecutar pip para instalar los requisitos
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', ruta_requisitos])
                print("Instalación completada exitosamente.")
            else:
                print("Las dependencias ya han sido instaladas.")
        except subprocess.CalledProcessError as e:
            print(f"Error durante la instalación: {e}")
    else:
        print(f"No se encontró el archivo {ruta_requisitos}")

if __name__ == "__main__":
    print("Instalando librerías...")
    instalar_requisitos()
    print("")
    input("PRESIONA ENTER PARA SALIR")
