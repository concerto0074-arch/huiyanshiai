import os
import re

def unify_ui():
    # 1. 从 index.html 提取标准组件 (仅提取模态框)
    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()

    # 更加精确提取模态框：从 <div ... id="ID"> 开始，匹配对应的平衡闭合标签
    def extract_modal(content, modal_id):
        # 匹配开始标签
        start_pattern = fr'<div[^>]+id="{modal_id}"[^>]*>'
        match = re.search(start_pattern, content)
        if not match: return ""
        
        start_idx = match.start()
        # 我们知道模态框通常有 3 级 div (modal > dialog > content)，但为了稳健，我们查找匹配的闭合标签
        # 简单方案：抓取直到下一个 modal 或特定的 anchor
        # 这里使用非贪婪匹配到第三个连续闭合 div 结束
        end_pattern = r'</div>\s*</div>\s*</div>'
        end_match = re.search(end_pattern, content[start_idx:])
        if not end_match: return ""
        
        return content[start_idx : start_idx + end_match.end()]

    login_m = extract_modal(index_content, 'loginModal')
    register_m = extract_modal(index_content, 'registerModal')
    user_info_m = extract_modal(index_content, 'userInfoModal')
    
    if not login_m: print("Warning: loginModal not found in index.html!")
    
    master_modals = f"{login_m}\n{register_m}\n{user_info_m}"
    toast_container = '<div id="toastContainer"></div>'

    # 提取 Premium 样式补丁
    style_patch_match = re.search(r'<style>([\s\S]*?\.modal-content[\s\S]*?)</style>', index_content)
    style_patch = style_patch_match.group(0) if style_patch_match else ""

    target_files = [
        'algorithms.html', 'products.html', 'group.html', 
        'experts.html', 'knowledge.html', 'cases.html', 'user_center.html'
    ]

    for filename in target_files:
        if not os.path.exists(filename): continue
            
        print(f"Final Polishing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # A. 清理：移除所有可能的残留
        content = re.sub(r'<div[^>]+id="loginModal"[\s\S]*?</div>\s*</div>\s*</div>', '', content)
        content = re.sub(r'<div[^>]+id="registerModal"[\s\S]*?</div>\s*</div>\s*</div>', '', content)
        content = re.sub(r'<div[^>]+id="userInfoModal"[\s\S]*?</div>\s*</div>\s*</div>', '', content)
        content = re.sub(r'<div class="modal-footer">[\s\S]*?立即注册</a>\s*</div>\s*</div>', '', content)
        content = re.sub(r'<div class="modal-footer">[\s\S]*?返回登录</a>\s*</div>\s*</div>', '', content)
        content = content.replace('<div id="toastContainer"></div>', '')

        # B. 重新注入模态框结构
        if '</body>' in content:
            content = content.replace('<script src="js/auth.js"></script>', '')
            insertion = f'\n{master_modals}\n{toast_container}\n<script src="js/auth.js"></script>\n</body>'
            content = content.replace('</body>', insertion)

        # C. 样式补丁注入
        if style_patch:
            content = re.sub(r'<style>[\s\S]*?\.modal-content[\s\S]*?</style>', '', content)
            content = content.replace('</head>', f'{style_patch}\n</head>')

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    print("Success: Final recovery completed. Site structure restored and cleaned.")

if __name__ == "__main__":
    unify_ui()
