import os
import json
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit

app = Flask(__name__)
# 秘密鍵を環境変数から取得する。環境変数が設定されていない場合は開発用にデフォルト値を使用。
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-random-fallback-secret-key')
socketio = SocketIO(app)

# Renderのデータベース接続URLを使用
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
db = SQLAlchemy(app)

# データベースのテーブルを定義
class CurrentAccess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(80), unique=True, nullable=False)

# データベースを初期化（初回デプロイ時のみ実行）
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """トップページを表示し、現在の入室人数を埋め込む"""
    try:
        # データベースから人数を取得
        current_count = CurrentAccess.query.count()
        
        # templates/index.html を読み込んで人数をレンダリングする
        return render_template('index.html', current_count=current_count)
    except FileNotFoundError:
        return "Error: index.html not found", 404

@app.route('/access', methods=['POST'])
def access_log():
    """入室・退室のコマンドを受け取り、データベースを更新する"""
    try:
        data = request.json
        device_id = data.get('deviceId')
        command = request.args.get('command')

        if not device_id or not command:
            return jsonify({'error': 'deviceId or command not provided'}), 400

        if command == 'enter':
            # すでに存在しない場合のみ追加
            existing_device = CurrentAccess.query.filter_by(device_id=device_id).first()
            if not existing_device:
                new_device = CurrentAccess(device_id=device_id)
                db.session.add(new_device)
                db.session.commit()
                message = "入室を記録しました"
            else:
                message = "既に入室済みです"
        elif command == 'exit':
            # 存在するデバイスレコードを1つ取得して削除
            existing_device = CurrentAccess.query.first() 
            if existing_device:
                db.session.delete(existing_device)
                db.session.commit()
                message = "退室を記録しました"
            else:
                message = "現在、入室中の人はいません"
        else:
            return jsonify({'error': 'Invalid command'}), 400
        
        current_count = CurrentAccess.query.count()
        
        # WebSocket経由で人数の更新を通知
        socketio.emit('update_count', {'count': current_count}) 

        return jsonify({'message': message, 'count': current_count}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WebSocket接続イベントハンドラ
@socketio.on('connect')
def test_connect():
    print('Client connected')

# アプリケーションの実行方法を修正
if __name__ == '__main__':
    # app.run()ではなく、socketio.run()を使用する
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
