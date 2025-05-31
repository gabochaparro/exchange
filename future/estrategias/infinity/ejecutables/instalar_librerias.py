import subprocess
import sys

def instalar_librerias():
    librerias = [
        'binance_connector',
        'binance_futures_connector',
        'colorama', 
        'gate_api',
        'gTTS',
        'kucoin_futures_python',
        'mutagen',
        'pandas',
        'paramiko',
        'Pillow',
        'pybit',
        'pygame',
        'pyinstaller',
        'python_binance',
        'python_bitget',
        'python_okx',
        'Requests',
        'websocket_client'
                ]  # Lista de librerías a instalar
    for libreria in librerias:
        subprocess.check_call([sys.executable, "-m", "pip", "install", libreria])

if __name__ == "__main__":
    try:
        print("Iniciando instalación de librerias...")
        instalar_librerias()
    except Exception as e:
        print("ERROR INSTALANDO LIBERIAS")
        print(e)
    input("PRESIONA ENTER PARA SALIR")