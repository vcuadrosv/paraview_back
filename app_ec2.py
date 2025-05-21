import os
import subprocess
import sys
import signal
import psutil  # Necesario para matar procesos hijos correctamente

# Verifica que se pasa el nombre del proyecto como argumento
if len(sys.argv) < 2:
    print("Error: Debes proporcionar el nombre del proyecto como argumento.")
    sys.exit(1)

project_name = sys.argv[1]
base_dir = f"/home/ubuntu/Simulaciones/{project_name}"
vtk_dir = os.path.join(base_dir, "VTK")
pid_file = "/tmp/paraviewweb.pid"

# Verifica si hay archivos VTK válidos
def has_vtk_files(directory):
    if not os.path.isdir(directory):
        return False
    for file in os.listdir(directory):
        if file.endswith(('.vtk', '.vtu', '.pvtu', '.pvd', '.vtm')):
            return True
    return False

if not has_vtk_files(vtk_dir):
    print(f"Error: No se encontraron archivos VTK válidos en {vtk_dir}")
    sys.exit(1)


# Mata proceso anterior si existe (y sus hijos, incluido Xvfb)
def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
        print(f"🔴 Terminando proceso anterior PID: {pid}")
    except (psutil.NoSuchProcess, ValueError):
        print(f"⚠️ Proceso anterior {pid} no existía")

if os.path.exists(pid_file):
    with open(pid_file, "r") as f:
        old_pid = f.read().strip()
    kill_process_tree(int(old_pid))
    os.remove(pid_file)
    
# Limpia locks de Xvfb por si quedaron de ejecuciones anteriores
x_lock = "/tmp/.X99-lock"
if os.path.exists(x_lock):
    os.remove(x_lock)
    print("🧹 Eliminado lock de Xvfb")

# Comando para ejecutar ParaViewWeb Visualizer
command = [
    "xvfb-run", "--auto-servernum","--server-num=99","-s", "-screen 0 1024x768x24",
    "~/ParaView-5.11.0-MPI-Linux-Python3.9-x86_64/bin/pvpython",
    "~/paraviewweb-visualizer/server/pvw-visualizer.py",
    "--content", "~/paraviewweb-visualizer/dist",
    "--port", "1234",
    "--data", vtk_dir,
    "--host", "0.0.0.0"
]
print(f"Comando: {command}")
# Directorio para logs
log_dir = "~/paraview_back/logs"
os.makedirs(log_dir, exist_ok=True)

stdout_path = os.path.join(log_dir, f"{project_name}_pvstdout.log")
stderr_path = os.path.join(log_dir, f"{project_name}_pvstderr.log")

# Ejecutar el comando
with open(stdout_path, "w") as out, open(stderr_path, "w") as err:
    print(f"Comando: {command}")
    process = subprocess.Popen(
        command,
        stdout=out,
        stderr=err,
        start_new_session=True  # 🔑 Mantiene el proceso vivo tras cerrar API
    )
    with open(pid_file, "w") as f:
        f.write(str(process.pid))

print(f"✅ Iniciando visualización de: {vtk_dir}")
print(f"🔁 PID del servidor pvpython: {process.pid}")