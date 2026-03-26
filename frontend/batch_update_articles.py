import os
import re

def synchronize_articles():
    # 1. 从 index.html 提取规范组件
    with open('index.html', 'r', encoding='utf-8') as f:
        index_content = f.read()

    # 提取 <head> 中的全局样式和脚本 (config.js 等)
    head_match = re.search(r'<head>(.*?)</head>', index_content, re.DOTALL)
    index_head = head_match.group(1) if head_match else ""
    # 过滤掉页面特定的 title 和少量特殊配置，保留通用部分
    index_head = re.sub(r'<title>.*?</title>', '', index_head)

    # 提取 <nav>
    nav_match = re.search(r'<nav.*?>.*?</nav>', index_content, re.DOTALL)
    index_nav = nav_match.group(0) if nav_match else ""
    # 确保导航栏中的 active 类在科普页是正确的
    index_nav = index_nav.replace('href="index.html" class="nav-link active"', 'href="index.html" class="nav-link"')
    index_nav = index_nav.replace('href="knowledge.html" class="nav-link"', 'href="knowledge.html" class="nav-link active"')

    # 提取 <footer>
    footer_match = re.search(r'<footer.*?>.*?</footer>', index_content, re.DOTALL)
    index_footer = footer_match.group(0) if footer_match else ""

    # 提取所有模态框 (loginModal, registerModal, userInfoModal)
    modals_match = re.findall(r'<div class="modal fade" id="(?:loginModal|registerModal|userInfoModal)".*?</div>\s*</div>\s*</div>', index_content, re.DOTALL)
    index_modals = "\n".join(modals_match)
    
    # 提取全局 Toast
    toast_match = re.search(r'<div id="toastContainer"></div>', index_content)
    index_toast = toast_match.group(0) if toast_match else ""

    # 2. 遍历所有文章详情页
    article_files = [f for f in os.listdir('.') if re.match(r'article-detail(-\d+)?\.html', f)]
    
    for filename in article_files:
        print(f"Processing {filename}...")
        with open(filename, 'r', encoding='utf-8') as f:
            art_content = f.read()

        # 提取原有文章的独特内容
        title_match = re.search(r'<title>(.*?)</title>', art_content)
        current_title = title_match.group(1) if title_match else "知识科普 - 慧眼识癌"
        
        main_content_match = re.search(r'<div class="main-content">.*?</div>\s*</div>\s*</div>', art_content, re.DOTALL)
        if not main_content_match:
            # 兼容不同结构的提取
            main_content_match = re.search(r'<!-- 主内容区 -->.*?<footer', art_content, re.DOTALL)
        
        current_main_content = main_content_match.group(0) if main_content_match else ""
        # 移除可能误抓的 footer 开始标签
        current_main_content = re.sub(r'<footer.*', '', current_main_content, flags=re.DOTALL).strip()

        # 3. 组装新页面
        new_page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{current_title}</title>
    {index_head}
    <style>
        /* 文章详情页专用补丁样式 */
        .main-content {{ padding: 40px 0; min-height: calc(100vh - 400px); background-color: #f8f9fa; }}
        .article-detail {{ background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-bottom: 40px; }}
        .back-btn {{ display: inline-flex; align-items: center; gap: 8px; padding: 10px 20px; background: #007BFF; color: #fff; border-radius: 5px; text-decoration: none; margin-bottom: 30px; transition: all 0.3s; }}
        .back-btn:hover {{ background: #0056b3; color: #fff; transform: translateX(-5px); }}
        .article-content img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 20px 0; }}
        .related-articles {{ background: #fff; padding: 30px; border-radius: 12px; margin-top: 40px; }}
    </style>
</head>
<body>
    {index_nav}
    
    {current_main_content}

    {index_footer}
    
    {index_modals}
    {index_toast}

    <script src="js/auth.js"></script>
</body>
</html>"""

        # 4. 写回文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_page)
            
    print("All article detail pages have been synchronized with index.html structure.")

if __name__ == "__main__":
    synchronize_articles()