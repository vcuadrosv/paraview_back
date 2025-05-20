from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import socket
import os
import psutil
import time

app = Flask(__name__)
CORS(app)

PORT_TO_KILL = 1234  # Puerto que usa ParaView
ACTIVE_PROJECTS = {}  # Mapeo: nombre_proyecto → PID

def kill_process_on_port(port, exclude_pid=None):
    """Mata procesos que usen el puerto, excepto uno opcional."""
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr.port == port and conn.pid:
            try:
                if conn.pid != exclude_pid:
                    p = psutil.Process(conn.pid)
                    print(f"🛑 Matando proceso {p.pid} en puerto {port}...")
                    p.terminate()
                    p.wait(timeout=3)
                    print("✅ Proceso terminado.")
            except Exception as e:
                print(f"⚠️ No se pudo terminar el proceso {conn.pid}: {e}")

@app.route('/start', methods=['POST'])
def start_backend():
    data = request.get_json()
    pressure = data.get('pressure')
    velocity = data.get('velocity')

    if pressure is None or velocity is None:
        return jsonify({
            'status': 'error',
            'message': 'Faltan parámetros: presión o velocidad'
        }), 400

    project = f"p_{pressure}_v{velocity}"
    print(f"🚀 Ejecutando app.py con proyecto: {project}")

    if project in ACTIVE_PROJECTS:
        pid = ACTIVE_PROJECTS[project]
        if psutil.pid_exists(pid):
            return jsonify({
                'status': 'ok',
                'message': f'{project} ya está en ejecución con PID {pid}'
            })
        else:
            del ACTIVE_PROJECTS[project]

    log_dir = "/home/ubuntu/paraview_back/logs"
    os.makedirs(log_dir, exist_ok=True)

    try:
        # Mata cualquier otro proceso en ese puerto excepto este mismo script
        kill_process_on_port(PORT_TO_KILL, exclude_pid=os.getpid())

        stdout_log = open(os.path.join(log_dir, f"{project}_stdout.log"), "w")
        stderr_log = open(os.path.join(log_dir, f"{project}_stderr.log"), "w")

        process = subprocess.Popen(
            ['python3', 'app_ec2.py', project],
            stdout=stdout_log,
            stderr=stderr_log,
            start_new_session=True
        )
        stdout_log.close()
        stderr_log.close()

        ACTIVE_PROJECTS[project] = process.pid
        print(f"✅ Lanzado app_ec2.py con PID {process.pid}")

        return jsonify({
            'status': 'ok',
            'message': f'app.py ejecutado con proyecto {project}, PID {process.pid}'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)