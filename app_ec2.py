import os
import subprocess
import sys

# Verifica que se pasa el nombre del proyecto como argumento
if len(sys.argv) < 2:
    print("Error: Debes proporcionar el nombre del proyecto como argumento.")
    sys.exit(1)

project_name = sys.argv[1]
base_dir = f"/home/ubuntu/Simulaciones/{project_name}"
vtk_dir = os.path.join(base_dir, "VTK")

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
    
# Comando para ejecutar ParaViewWeb Visualizer
command = [
    "xvfb-run", "-s", "-screen 0 1024x768x24",
    "/home/ubuntu/ParaView-5.11.0-MPI-Linux-Python3.9-x86_64/bin/pvpython",
    "/home/ubuntu/paraviewweb-visualizer/server/pvw-visualizer.py",
    "--content", "/home/ubuntu/paraviewweb-visualizer/dist",
    "--port", "1234",
    "--data", vtk_dir,
    "--host", "0.0.0.0"
]

# Ejecutar el comando
# Directorio para logs
log_dir = "/home/ubuntu/paraview_back/logs"
os.makedirs(log_dir, exist_ok=True)

stdout_path = os.path.join(log_dir, f"{project_name}_pvstdout.log")
stderr_path = os.path.join(log_dir, f"{project_name}_pvstderr.log")

with open(stdout_path, "w") as out, open(stderr_path, "w") as err:
    process = subprocess.Popen(
        command,
        stdout=out,
        stderr=err,
        start_new_session=True  # 🔑 ESTO es lo que lo mantiene vivo
    )

print(f"✅ Iniciando visualización de: {vtk_dir}")
print(f"🔁 PID del servidor pvpython: {process.pid}")