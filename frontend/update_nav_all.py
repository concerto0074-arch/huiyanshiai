import os
import re

# 获取当前目录下所有article-detail*.html文件
files = [f for f in os.listdir('.') if f.startswith('article-detail') and f.endswith('.html')]

# 定义正则表达式模式，匹配团体方案导航项
pattern = re.compile(r'(<li\s+class="nav-item">\s*<a\s+class="nav-link"\s+href="group\.html">团体方案</a>\s*</li>)', re.IGNORECASE)

# 遍历所有文件
for filename in files:
    print(f'Processing file: {filename}')
    
    # 打开文件并读取内容
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 检查文件是否已经包含算法导航项
    if '核心算法' in content:
        print(f'✓ {filename} already contains algorithm nav item, skipping...')
        continue
    
    # 查找匹配项
    match = pattern.search(content)
    if match:
        # 构建算法导航项
        algorithm_nav = '''                    <li class="nav-item">
                        <a class="nav-link" href="algorithms.html">核心算法</a>
                    </li>'''
        
        # 插入算法导航项
        updated_content = pattern.sub(f'\1\n{algorithm_nav}', content)
        
        # 写入更新后的内容
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print(f'✓ {filename} updated successfully!')
    else:
        print(f'✗ Could not find group nav item in {filename}')

print('\nAll files processed!')