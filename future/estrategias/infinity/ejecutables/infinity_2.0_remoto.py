import os
import subprocess

def abrir_terminal_y_conectar():
    # Directorio local donde se generará el script temporal
    directorio = "/Volumes/Datos/DESARROLLO PERSONAL/PROGRAMAR APLICACIONES WEB/Perfeccionar Python/Proyectos Python/Trading Bot Exchange/exchange/future/estrategias/infinity"
    
    # Comandos remotos que se ejecutarán después de la conexión SSH
    comandos_remotos = """
        cd exchange
        source entorno/bin/activate
        python3 future/estrategias/infinity/infinity_2.0.py
    """
    
    # Comando SSH que incluye los comandos remotos
    comando_ssh = (
        f'ssh -i "clave_pen_ec2_01.pem" ubuntu@ec2-15-228-57-72.sa-east-1.compute.amazonaws.com '
        f'"{comandos_remotos.strip()}"'
    )
    
    # Crear un script bash para ejecutar el comando en la terminal
    script_path = os.path.join(directorio, "abrir_terminal.sh")
    
    with open(script_path, "w") as script_file:
        script_file.write(f"#!/bin/bash\n")
        script_file.write(f"cd '{directorio}'\n")
        script_file.write(f"{comando_ssh}\n")
    
    # Asegurarse de que el script sea ejecutable
    os.chmod(script_path, 0o755)
    
    # Abrir la terminal y ejecutar el script
    subprocess.run(["open", "-a", "Terminal", script_path])

if __name__ == "__main__":
    abrir_terminal_y_conectar()
