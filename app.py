import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)
DATA_FILE = 'data.json'

# data.jsonが存在しない場合は作成し、初期データを書き込む
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({'current_access': []}, f)

@app.route('/')
def index():
    """トップページを表示し、現在の入室人数を埋め込む"""
    try:
        with open(DATA_FILE, 'r') as f:
            log_data = json.load(f)
        current_count = len(log_data.get('current_access', []))
        
        # HTMLファイルを読み込んで人数を埋め込む
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        return html_content.replace('{{ current_count }}', str(current_count))
    except FileNotFoundError:
        return "Error: index.html not found", 404
    except json.JSONDecodeError:
        return "Error: Invalid JSON format in data.json", 500

@app.route('/access', methods=['POST'])
def access_log():
    """入室・退室のコマンドを受け取り、記録を更新する"""
    try:
        data = request.json
        device_id = data.get('deviceId')
        command = request.args.get('command') # <-- URLパラメータからcommandを取得

        if not device_id or not command:
            return jsonify({'error': 'deviceId or command not provided'}), 400

        with open(DATA_FILE, 'r+') as f:
            log_data = json.load(f)
            
            if command == 'enter':
                if device_id not in log_data['current_access']:
                    log_data['current_access'].append(device_id)
                    message = "入室を記録しました"
                else:
                    message = "既に入室済みです"
            elif command == 'exit':
                if device_id in log_data['current_access']:
                    log_data['current_access'].remove(device_id)
                    message = "退室を記録しました"
                else:
                    message = "既に入室していません"
            else:
                return jsonify({'error': 'Invalid command'}), 400

            # ファイルを最初から書き直す
            f.seek(0)
            json.dump(log_data, f, indent=4)
            f.truncate()

        return jsonify({'message': message, 'count': len(log_data['current_access'])}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
