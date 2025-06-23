from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt
from functools import wraps
from flask_cors import CORS
import os
import json
import threading
import control as control
from controlsinraps import auto_mode_worker, guardar_reporte, actualizar_nivel, dispensar
from datetime import datetime , timedelta

app = Flask(__name__)
CORS(app)

SECRET_KEY = "supersecretkey"
USER_FILE = './archivos/usuarios.json'
CONFIG_FILE = './archivos/autoconfiguracion.json'
REPORT_FILE = './archivos/reportes.json'
NIVEL_FILE = './archivos/nivel_alimento.json'

# Inicialización
def init_file(path, default):
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump(default, f)

init_file(USER_FILE, [])
init_file(REPORT_FILE, [])
init_file(CONFIG_FILE, {'hora_inicio': '', 'intervalo': 0, 'raciones': 0})
init_file(NIVEL_FILE, {'nivel': 90})


# JWT Middleware
def token_required(f):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token missing"}), 401
        try:
            token = token.split()[1]
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({"message": "Invalid token"}), 401
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


# Endpoints
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    email = data.get('email')

    with open(USER_FILE, 'r+') as f:
        users = json.load(f)
        if any(u['username'] == username for u in users):
            return jsonify({"message": "Usuario ya existe"}), 400

        users.append({
            'username': username,
            'password': generate_password_hash(password),
            'name': name,
            'email': email
        })
        f.seek(0)
        json.dump(users, f)
        f.truncate()

    return jsonify({"message": "Usuario registrado correctamente"}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    with open(USER_FILE, 'r') as f:
        users = json.load(f)

    for user in users:
        if user['username'] == username and check_password_hash(user['password'], password):
            token = jwt.encode({
                'user': username,
                'exp': datetime.utcnow() + timedelta(hours=2)
            }, SECRET_KEY, algorithm="HS256")
            return jsonify({"token": token}), 200

    return jsonify({"message": "Credenciales inválidas"}), 401

@app.route('/auto-configu', methods=['GET'])

def get_auto_config():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return jsonify(config)

@app.route('/auto-config', methods=['POST'])

def set_auto_config():
    data = request.json
    config = {
        'hora_inicio': data.get('hora_inicio'),
        'intervalo': data.get('intervalo'),
        'raciones': data.get('raciones')
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    return jsonify({'message': 'Configuración guardada exitosamente', 'config': config})





@app.route('/manual-feed', methods=['POST'])
@token_required
def manual_feed():
    data = request.get_json()
    porciones = data.get("porciones")
    now = datetime.now()
    
    if porciones is None:
        return jsonify({"mensaje": "Cantidad no especificada"}), 400
    
    dispensar(porciones)
    guardar_reporte(now, porciones, 'manual')
    actualizar_nivel(int(porciones))
    return jsonify({"mensaje": f"Se dispensaron {porciones} porciones manualmente."})


@app.route('/estado', methods=['POST'])
@token_required
def estado():
    with open(NIVEL_FILE, 'r') as f:
        data = json.load(f)
    return jsonify({'nivel': data['nivel'], 'estado': 'Modo automático activo. Próxima dispensación programada.'})


@app.route('/reportes', methods=['POST'])
@token_required
def reportes():
    with open(REPORT_FILE, 'r') as f:
        data = json.load(f)
    return jsonify({'registros': data[::-1]})



@app.route('/rellenar', methods=['PATCH'])
@token_required
def recargar():
    try:
        with open(NIVEL_FILE, 'w') as f:
            json.dump({'nivel': 100}, f)
        return jsonify({'msg': 'Nivel restablecido a 100%'}), 200
    except Exception as e:
        return jsonify({'msg': f'Error al rellenar: {str(e)}'}), 500


def iniciar_servidor():
    threading.Thread(target=auto_mode_worker, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)


if __name__ == '__main__':
    iniciar_servidor()