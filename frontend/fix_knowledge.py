import os
import re

def fix_knowledge_and_articles():
    # 1. 修复 knowledge.html 中的重复模态框
    with open('knowledge.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # 移除末尾重复的模态框块
    # 识别逻辑：如果出现了多次 id="loginModal"，保留最后一个或者第一个
    # 我们之前的 unify_site_ui.py 是在 </body> 前插入的。
    # 彻底清理：移除所有模态框，然后重新从 index.html 获取并插入一次。
    
    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    modals_match = re.findall(r'<div class="modal fade" id="(?:loginModal|registerModal|userInfoModal)".*?</div>\s*</div>\s*</div>', index_content, re.DOTALL)
    master_modals = "\n".join(modals_match)
    master_toast = '<div id="toastContainer"></div>'

    # 移除现有所有模态框
    content = re.sub(r'<div class="modal fade" id="(?:loginModal|registerModal|userInfoModal)".*?</div>\s*</div>\s*</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'<div id="toastContainer"></div>', '', content)
    
    # 重新插入
    content = content.replace('</body>', f'{master_modals}\n{master_toast}\n<script src="js/auth.js"></script>\n</body>')
    
    with open('knowledge.html', 'w', encoding='utf-8') as f:
        f.write(content)

    # 2. 补全缺失的 article-detail-*.html (13-20)
    for i in range(13, 21):
        filename = f'article-detail-{i}.html'
        if not os.path.exists(filename):
            print(f"Creating placeholder for {filename}...")
            # 使用 article-detail.html 作为模板
            with open('article-detail.html', 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 更新标题
            template = re.sub(r'<title>.*?</title>', f'<title>知识详情 {i} - 慧眼识癌</title>', template)
            template = re.sub(r'<h1 id="article-title">.*?</h1>', f'<h1 id="article-title">深度科普：癌症研究的新前沿 {i}</h1>', template)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(template)

    print("Knowledge page fixed and missing articles created.")

if __name__ == "__main__":
    fix_knowledge_and_articles()
