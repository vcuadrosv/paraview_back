import os
import subprocess
import time
import socket
import sys

# Leer argumento del nombre del subdirectorio
with open("debug.log", "a") as f:
    f.write(f" Lanzado con argumentos: {sys.argv}\n")

if len(sys.argv) < 2:
    print(" Error: Debes proporcionar el nombre del proyecto como argumento.")
    sys.exit(1)

project_folder = sys.argv[1]

# Ruta base general
ROOT_DIR = r"D:\Valery_v\desarrollo\Simulaciones"

# Ruta al proyecto
BASE_DIR = os.path.join(ROOT_DIR, project_folder)

# Ruta a ParaView
PARAVIEW_BIN_DIR = r"D:\Programas\ParaView 5.11.0\bin"
PORT = 1234  # Puedes cambiar el puerto si es necesario

# Verificar si el directorio base existe
if not os.path.exists(BASE_DIR):
    print(f" Error: El directorio base '{BASE_DIR}' no existe.")
    sys.exit(1)

vtk_dir = os.path.join(BASE_DIR, "VTK")  # Ruta a la carpeta VTK

# Verificar si la carpeta VTK existe y contiene archivos VTK válidos
def has_vtk_files(directory):
    valid_extensions = ['.vtk', '.vtu', '.pvtu', '.pvd', '.vtm']
    for file in os.listdir(directory):
        if any(file.endswith(ext) for ext in valid_extensions):
            return True
    return False

if os.path.exists(vtk_dir) and has_vtk_files(vtk_dir):
    print(f" VTK encontrado en {vtk_dir}, listo para visualizar.")
else:
    print(f" Error: La carpeta {vtk_dir} no existe o no contiene archivos VTK válidos.")
    sys.exit(1)

# Verificar que pvpython.exe está instalado
pvpython_path = os.path.join(PARAVIEW_BIN_DIR, "pvpython.exe")
if not os.path.exists(pvpython_path):
    print(f" Error: No se encontró ParaView en '{pvpython_path}'. Verifica la instalación.")
    sys.exit(1)

# Verificar si el puerto está ocupado
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

if is_port_in_use(PORT):
    print(f" Error: El puerto {PORT} ya está en uso. Intenta con otro.")
    sys.exit(1)

# Iniciar el servidor ParaView Web
server_command = [
    pvpython_path,
    "-m", "paraview.apps.visualizer",
    "--data", vtk_dir,
    "--port", str(PORT)
]

try:
    server_process = subprocess.Popen(server_command)
    time.sleep(3)  # Dar tiempo a que el servidor inicie
    print(f"\n Servidor ParaView Web iniciado en el puerto {PORT}")
    print(f" Accede en: http://localhost:{PORT}/")
except Exception as e:
    print(f" Error al iniciar ParaView Web: {e}")
