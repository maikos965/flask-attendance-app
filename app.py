from flask import Flask, send_from_directory, request, jsonify
import json
import os

app = Flask(__name__)

# data.json の新しいパス
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    # index.html を提供
    return send_from_directory('..', 'index.html')

@app.route('/login')
def login():
    # login.html を提供
    return send_from_directory('..', 'login.html')

@app.route('/data/<path:filename>')
def serve_data_static(filename):
    # data フォルダ内の静的ファイルを提供
    return send_from_directory('.', filename)

@app.route('/login/<path:filename>')
def serve_login_static(filename):
    # login フォルダ内の静的ファイルを提供
    return send_from_directory('../login', filename)

@app.route('/access', methods=['POST'])
def access():
    device_id = request.json.get('deviceId')
    if not device_id:
        return jsonify({'status': 'error', 'message': 'Device ID is required'}), 400

    data = load_data()

    if device_id in data:
        data.remove(device_id)
        save_data(data)
        return jsonify({'status': 'logout', 'message': '退出しました'})
    else:
        data.append(device_id)
        save_data(data)
        return jsonify({'status': 'login', 'message': '入室しました'})

@app.route('/count', methods=['GET'])
def count():
    # 入室人数を返す
    data = load_data()
    return jsonify({'count': len(data)})

if __name__ == '__main__':
    app.run(debug=True)