"""
去掉导航栏下拉菜单的三角箭头（dropdown caret），
通过在悬停CSS块中追加隐藏caret的规则实现。
"""
import os

OLD_CSS_MARKER = '.dropdown-item:hover { background-color: #f0f7ff; color: #007BFF; }'
NEW_CSS_BLOCK = """.dropdown-item:hover { background-color: #f0f7ff; color: #007BFF; }
        /* 隐藏下拉箭头，更简洁 */
        .navbar .dropdown-toggle::after { display: none; }"""

def process(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if OLD_CSS_MARKER in content and 'dropdown-toggle::after' not in content:
        content = content.replace(OLD_CSS_MARKER, NEW_CSS_BLOCK)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[OK] {os.path.basename(filepath)}')
    else:
        print(f'[SKIP] {os.path.basename(filepath)}')

if __name__ == '__main__':
    html_dir = r'd:\huiyanshiai(2.0)\frontend'
    for f in sorted(os.listdir(html_dir)):
        if f.endswith('.html'):
            process(os.path.join(html_dir, f))
