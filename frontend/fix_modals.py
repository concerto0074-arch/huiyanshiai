import os
import re

dir_path = r'd:\huiyanshiai(2.0)\frontend'

def fix_file(filename):
    file_path = os.path.join(dir_path, filename)
    if not os.path.exists(file_path): return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Fix duplicate navbar in pagination (specifically cases.html)
    match = re.search(r'<!-- 分页控件 -->\s*<div class=\"pagination-container mt-4\">\s*<nav class=\"navbar.*?</nav>\s*</div>', content, flags=re.DOTALL)
    if match:
        content = content[:match.start()] + '<!-- 分页控件 -->\n        <div class="pagination-container mt-4">\n        </div>' + content[match.end():]

    # 2. Extract good modals from login_template.html
    template_path = os.path.join(dir_path, 'login_template.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    modal_start = template_content.find('<!-- 登录模态框 -->')
    modal_end = template_content.find('<!-- 登录注册功能 JavaScript -->')
    good_modals = template_content[modal_start:modal_end].strip()

    # 3. Replace broken modal at the bottom
    broken_start = content.find('<!-- 登录模态框 -->')
    if broken_start != -1:
        # Find where to stop replacing
        end_script = content.find('<script src="https://cdn.jsdelivr.net', broken_start)
        if end_script == -1:
            end_script = content.find('</body>', broken_start)
        
        # Replace
        content = content[:broken_start] + good_modals + '\n    \n    ' + content[end_script:]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Fixed {filename}')

files_to_fix = ['cases.html', 'experts.html', 'group.html', 'knowledge.html', 'products.html', 'algorithms.html']
for f in files_to_fix:
    fix_file(f)

# Also ensure index.html gets its full feature set if loginModal is missing
index_path = os.path.join(dir_path, 'index.html')
with open(index_path, 'r', encoding='utf-8') as f:
    idx_content = f.read()

if 'id="loginModal"' not in idx_content:
    print("Fixing index.html to include loginModal")
    # Insert before <div class="modal fade" id="registerModal"
    ins_point = idx_content.find('<div class="modal fade" id="registerModal"')
    if ins_point != -1:
        # Get just the loginModal part
        tmp_content = template_content[modal_start:template_content.find('<!-- 注册模态框 -->')].strip()
        idx_content = idx_content[:ins_point] + tmp_content + '\n    ' + idx_content[ins_point:]
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(idx_content)

print('All fixed')
