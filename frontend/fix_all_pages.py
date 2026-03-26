import os
import re

def fix_all_pages():
    target_files = [
        'algorithms.html', 'products.html', 'group.html', 
        'experts.html', 'knowledge.html', 'cases.html', 'user_center.html'
    ]
    
    # 补全缺失的详情页
    for i in range(1, 21):
        target_files.append(f'article-detail-{i}.html')
    target_files.append('article-detail.html')

    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    modals_match = re.findall(r'<div class="modal fade" id="(?:loginModal|registerModal|userInfoModal)".*?</div>\s*</div>\s*</div>', index_content, re.DOTALL)
    master_modals = "\n".join(modals_match)
    master_toast = '<div id="toastContainer"></div>'

    for filename in target_files:
        if not os.path.exists(filename):
            continue
            
        print(f"Fixing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. 移除现有模态框、Toast 和 auth.js
        content = re.sub(r'<div class="modal fade" id="(?:loginModal|registerModal|userInfoModal)".*?</div>\s*</div>\s*</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div id="toastContainer"></div>', '', content)
        content = re.sub(r'<script\s+src="js/auth.js"></script>', '', content)
        
        # 2. 重新在 </body> 前插入一份干净的
        # 移除末尾多余的空行
        content = content.strip()
        if '</body>' in content:
            content = content.replace('</body>', f'{master_modals}\n{master_toast}\n<script src="js/auth.js"></script>\n</body>')
        else:
            content += f'\n{master_modals}\n{master_toast}\n<script src="js/auth.js"></script>\n'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    print("All pages sanitized.")

if __name__ == "__main__":
    fix_all_pages()
