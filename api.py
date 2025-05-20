from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import socket
import psutil  # ← Necesitamos esta librería para gestionar procesos

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas las rutas

PORT_TO_KILL = 1234  # Puerto que usará ParaView

def kill_process_on_port(port):
    """Mata cualquier proceso que esté usando el puerto especificado."""
    for conn in psutil.net_connections():
        if conn.laddr.port == port:
            pid = conn.pid
            if pid:
                try:
                    p = psutil.Process(pid)
                    print(f"🛑 Matando proceso {pid} que usa el puerto {port}...")
                    p.terminate()
                    p.wait(timeout=3)
                    print("✅ Proceso terminado.")
                except Exception as e:
                    print(f"⚠️ No se pudo terminar el proceso {pid}: {e}")

@app.route('/start', methods=['POST'])
def start_backend():
    data = request.get_json()
    pressure = data.get('pressure')
    velocity = data.get('velocity')

    if pressure is None or velocity is None:
        return jsonify({
            'status': 'error',
            'message': 'Faltan parámetros: presión o velocidad'
        })

    # Generar nombre del proyecto
    project = f"p_{pressure}_v{velocity}"
    print(f"🚀 Ejecutando app.py con proyecto: {project}")

    # Matar cualquier proceso que use el puerto antes de lanzar
    kill_process_on_port(PORT_TO_KILL)

    try:
        result = subprocess.run(
            ['python', 'app_ec2.py', project], #app.py para local y app_ec2.py para ec2.
            capture_output=True,
            text=True
        )

        print("📤 STDOUT:\n", result.stdout)
        print("📥 STDERR:\n", result.stderr)

        if result.returncode == 0:
            return jsonify({
                'status': 'ok',
                'message': f'app.py ejecutado con proyecto {project}'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Error al ejecutar app.py:\n{result.stderr}'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)