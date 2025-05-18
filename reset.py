import json
import os

# data.json のパス
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

# 空リストに初期化
with open(DATA_FILE, 'w') as f:
    json.dump([], f)

print("入室データをリセットしました。")
