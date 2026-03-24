import os

# 获取所有HTML文件
html_files = [f for f in os.listdir('.') if f.endswith('.html')]

# 导航栏中应该包含的"算法"选项
algorithm_nav_item = '<li class="nav-item">\n                        <a class="nav-link" href="algorithms.html">核心算法</a>\n                    </li>'

# 遍历所有HTML文件
for file_name in html_files:
    # 跳过登录模板和管理登录页面
    if file_name in ['login_template.html', 'admin_login.html']:
        continue
    
    print(f"处理文件: {file_name}")
    
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查导航栏中是否已经包含"核心算法"
        if '核心算法' in content:
            print(f"  ✓ 已包含核心算法选项")
            continue
        
        # 查找导航栏结束位置，更简单的方法
        nav_end_index = content.find('</ul>', content.find('<ul class="navbar-nav mx-auto">'))
        if nav_end_index != -1:
            # 替换导航栏结束标记，添加算法选项
            new_content = content[:nav_end_index] + f'\n                    {algorithm_nav_item}' + content[nav_end_index:]
            
            # 写回文件
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  ✓ 已添加核心算法选项")
        else:
            print(f"  ✗ 未找到导航栏结束位置")
    except Exception as e:
        print(f"  ✗ 处理失败: {e}")

print("所有文件处理完成！")