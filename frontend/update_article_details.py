import os
import re

# 设置文件路径
template_path = os.path.join(os.getcwd(), 'article-detail.html')

# 读取模板文件内容
with open(template_path, 'r', encoding='utf-8') as f:
    template_content = f.read()

# 提取登录模态框部分（从<!-- 登录模态框 -->到<!-- 用户信息模态框 -->）
login_modal_pattern = r'<!-- 登录模态框 -->.*?<!-- 用户信息模态框 -->'
login_modal_content = re.search(login_modal_pattern, template_content, re.DOTALL).group(0)

# 提取JavaScript函数部分（从// 登录/注册相关函数到// 页面加载完成后执行）
js_functions_pattern = r'// 登录/注册相关函数.*?// 页面加载完成后执行'
js_functions_content = re.search(js_functions_pattern, template_content, re.DOTALL).group(0)

# 获取所有article-detail-*.html文件
article_files = [f for f in os.listdir('.') if re.match(r'article-detail-\d+\.html', f)]

# 遍历所有文件并更新
for file_name in article_files:
    print(f'正在更新 {file_name}...')
    file_path = os.path.join(os.getcwd(), file_name)
    
    # 读取当前文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换登录/注册模态框部分
    content = re.sub(r'<!-- 登录/注册模态框 -->.*?<!-- 用户信息模态框 -->', login_modal_content, content, flags=re.DOTALL)
    
    # 替换JavaScript函数部分
    content = re.sub(r'// 登录/注册相关函数.*?// 页面加载完成后执行', js_functions_content, content, flags=re.DOTALL)
    
    # 保存修改后的文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'已更新 {file_name}')

print('所有article-detail*.html页面已更新完成！')