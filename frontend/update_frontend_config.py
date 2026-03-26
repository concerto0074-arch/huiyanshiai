import os
import re

CONFIG_PATH = r'd:\huiyanshiai(2.0)\frontend\config.js'

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# 强制将 backendUrl 设置为 http://localhost:5000，不再区分 isLocal
# 原本逻辑: const backendUrl = isLocal ? "http://localhost:5001" : PRODUCTION_API_URL;
pattern = r'const backendUrl = isLocal \? "http://localhost:5001" : PRODUCTION_API_URL;'
replacement = 'const backendUrl = "http://localhost:5000"; // 统一由 5000 端口提供服务'

new_content = re.sub(pattern, replacement, content)

if new_content != content:
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Frontend config updated: all points to 5000")
else:
    print("Could not find patterns to update in frontend config")
