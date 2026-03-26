import os
import re

def unify_ui():
    # 1. 从 index.html 提取标准组件
    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()

    # 提取 <nav>
    nav_match = re.search(r'<nav.*?>.*?</nav>', index_content, re.DOTALL)
    master_nav = nav_match.group(0) if nav_match else ""

    # 提取 <footer>
    footer_match = re.search(r'<footer.*?>.*?</footer>', index_content, re.DOTALL)
    master_footer = footer_match.group(0) if footer_match else ""

    # 提取模态框 (loginModal, registerModal, userInfoModal)
    modals_match = re.findall(r'<div class="modal fade" id="(?:loginModal|registerModal|userInfoModal)".*?</div>\s*</div>\s*</div>', index_content, re.DOTALL)
    master_modals = "\n".join(modals_match)
    
    # 提取 Toast Container
    toast_container = '<div id="toastContainer"></div>'

    # 提取 <head> 中的相关配置脚本 (config.js) 和样式补丁
    # 特别是针对登录模态框的样式补丁
    style_patch_match = re.search(r'<style>\s*/\* 优化登录/注册模态框.*?/style>', index_content, re.DOTALL)
    style_patch = style_patch_match.group(0) if style_patch_match else ""

    # 2. 定义目标文件列表
    target_files = [
        'algorithms.html', 'products.html', 'group.html', 
        'experts.html', 'knowledge.html', 'cases.html', 'user_center.html'
    ]

    for filename in target_files:
        if not os.path.exists(filename):
            continue
            
        print(f"Updating UI for {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # A. 替换导航栏
        content = re.sub(r'<nav.*?>.*?</nav>', master_nav, content, flags=re.DOTALL)
        
        # 为当前页面设置 active 类
        # 清除所有 active
        content = content.replace('nav-link active', 'nav-link')
        # 根据文件名设置 active
        if filename == 'algorithms.html':
            content = content.replace('href="algorithms.html" class="nav-link"', 'href="algorithms.html" class="nav-link active"')
        elif filename == 'products.html':
            content = content.replace('href="products.html" class="nav-link"', 'href="products.html" class="nav-link active"')
        elif filename == 'group.html':
            content = content.replace('href="group.html" class="nav-link"', 'href="group.html" class="nav-link active"')
        elif filename == 'experts.html':
            content = content.replace('href="experts.html" class="nav-link"', 'href="experts.html" class="nav-link active"')
        elif filename == 'knowledge.html':
            content = content.replace('href="knowledge.html" class="nav-link"', 'href="knowledge.html" class="nav-link active"')
        elif filename == 'cases.html':
            content = content.replace('href="cases.html" class="nav-link"', 'href="cases.html" class="nav-link active"')

        # B. 替换页脚
        content = re.sub(r'<footer.*?>.*?</footer>', master_footer, content, flags=re.DOTALL)

        # C. 替换模态框
        # 先移除现有的模态框
        content = re.sub(r'<div class="modal fade" id="loginModal".*?</div>\s*</div>\s*</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="modal fade" id="registerModal".*?</div>\s*</div>\s*</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="modal fade" id="userInfoModal".*?</div>\s*</div>\s*</div>', '', content, flags=re.DOTALL)
        
        # 在 </body> 前插入新模态框和 Toast
        if '</body>' in content:
            # 确保不重复插入
            if 'id="loginModal"' not in content:
                content = content.replace('</body>', f'{master_modals}\n{toast_container}\n<script src="js/auth.js"></script>\n</body>')
            else:
                # 如果已经有了，就更新它
                # 这种逻辑比较复杂，简单起见，如果正则替换没清干净，手动定位插入
                pass

        # D. 插入样式补丁到 <head>
        if style_patch and style_patch[:20] not in content:
            content = content.replace('</head>', f'{style_patch}\n</head>')

        # E. 确保引入 config.js 和 auth.js
        if 'src="config.js"' not in content:
            content = content.replace('</head>', '<script src="config.js"></script>\n</head>')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)

    print("Site-wide UI unification complete.")

if __name__ == "__main__":
    unify_ui()
