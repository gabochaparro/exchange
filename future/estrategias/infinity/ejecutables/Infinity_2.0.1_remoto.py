import subprocess

def abrir_conexion_ec2_y_ejecutar():
    # Ruta local y comando para conexión SSH
    ruta_local = '/Volumes/Datos/DESARROLLO PERSONAL/PROGRAMAR APLICACIONES WEB/Perfeccionar Python/Proyectos Python/Trading Bot Exchange/exchange/future/estrategias/infinity/'
    ssh_comando = 'ssh -i "clave_pen_ec2_01.pem" ubuntu@ec2-15-228-57-72.sa-east-1.compute.amazonaws.com'

    # Comandos a ejecutar dentro del servidor EC2
    comandos_remotos = [
        'cd exchange',
        'source entorno/bin/activate',
        'python3 future/estrategias/infinity/infinity_2.0.py'
    ]
    comando_remoto_unido = " && ".join(comandos_remotos)

    # Comando completo
    comando_ssh = f'cd "{ruta_local}" && {ssh_comando} "{comando_remoto_unido}"'

    try:
        # Ejecutar el comando en la terminal
        subprocess.run(comando_ssh, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e}")

if __name__ == "__main__":
    abrir_conexion_ec2_y_ejecutar()
