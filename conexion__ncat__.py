import subprocess

def start_ncat_server():
    try:
        subprocess.run(["ncat", "-lvnp", "9001"], check=True)
        print("El servidor ncat ha sido detenido.")
        
    except subprocess.CalledProcessError as e:
        print("Error al ejecutar el comando:", e)
    except KeyboardInterrupt:
        print("El servidor ncat ha sido detenido.")

start_ncat_server()
