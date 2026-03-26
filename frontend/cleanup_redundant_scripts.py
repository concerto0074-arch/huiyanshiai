import os
import re

def cleanup_scripts():
    target_files = [
        'algorithms.html', 'products.html', 'group.html', 
        'experts.html', 'knowledge.html', 'cases.html', 'user_center.html'
    ]

    for filename in target_files:
        if not os.path.exists(filename):
            continue
            
        print(f"Cleaning scripts for {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 移除重复定义的 checkLoginStatus, showLoginModal, showRegisterModal 等
        # 这些现在都在 auth.js 中统一处理了
        redundant_functions = [
            r'function\s+checkLoginStatus\s*\(\)\s*\{.*?\}',
            r'function\s+showLoginModal\s*\(\)\s*\{.*?\}',
            r'function\s+showRegisterModal\s*\(\)\s*\{.*?\}',
            r'function\s+logout\s*\(\)\s*\{.*?\}',
            r'function\s+login\s*\(\)\s*\{.*?\}',
            r'function\s+register\s*\(\)\s*\{.*?\}'
        ]
        
        # 特殊情况：user_center.html 需要保留对中心区域 UI 的更新，但不要冲突全局函数
        if filename == 'user_center.html':
            # 只重命名内部的 checkLoginStatus 为 updateDashboardUserInfo
            content = content.replace('checkLoginStatus()', 'updateDashboardUserInfo()')
            content = content.replace('function checkLoginStatus()', 'function updateDashboardUserInfo()')
        else:
            for pattern in redundant_functions:
                content = re.sub(pattern, '', content, flags=re.DOTALL)

        # 移除重复的 script 标签
        content = re.sub(r'<script\s+src="js/auth.js"></script>\s*<script\s+src="js/auth.js"></script>', '<script src="js/auth.js"></script>', content)

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    print("Script cleanup complete.")

if __name__ == "__main__":
    cleanup_scripts()
