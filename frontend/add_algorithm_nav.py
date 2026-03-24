import os
import re

# 获取所有HTML文件
html_files = [f for f in os.listdir('.') if f.endswith('.html')]

# 导航栏中应该包含的"算法"选项
algorithm_nav_item = '<li class="nav-item">\n                        <a class="nav-link" href="algorithms.html">核心算法</a>\n                    </li>'

# 导航栏结束标记
nav_end_pattern = '</ul>'

# 遍历所有HTML文件
for file_name in html_files:
    # 跳过登录模板和管理登录页面
    if file_name in ['login_template.html', 'admin_login.html']:
        continue
    
    with open(file_name, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查导航栏中是否已经包含"核心算法"
    if '核心算法' in content:
        print(f"{file_name}: 已包含核心算法选项")
        continue
    
    # 查找导航栏结束位置
    nav_end_match = re.search(r'</ul>.*?</nav>', content, re.DOTALL)
    if nav_end_match:
        # 替换导航栏结束标记，添加算法选项
        new_content = content.replace('</ul>', f'                    {algorithm_nav_item}\n                </ul>')
        
        # 写回文件
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"{file_name}: 已添加核心算法选项")
    else:
        print(f"{file_name}: 未找到导航栏结束位置")

print("所有文件处理完成！")