#!/usr/bin/env python3
import os

# 读取products.html中的标准登录组件
def get_standard_components():
    with open('products.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取登录模态框
    login_start = content.find('<!-- 登录模态框 -->')
    user_info_start = content.find('<!-- 用户信息模态框 -->')
    login_modal = content[login_start:user_info_start]
    
    # 提取login()函数
    login_start = content.find('function login()')
    login_end = content.find('function register()', login_start)
    login_func = content[login_start:login_end].strip()
    
    # 确保提取到完整的函数
    if '}' not in login_func:
        # 查找函数结束括号
        temp_content = content[login_start:]
        brace_count = 0
        for i, char in enumerate(temp_content):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    login_func = temp_content[:i+1]
                    break
    
    return login_modal, login_func

# 更新文件中的登录组件
def update_file(filename, login_modal, login_func):
    print(f"正在更新: {filename}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新登录模态框
    login_start = content.find('<!-- 登录模态框 -->')
    user_info_start = content.find('<!-- 用户信息模态框 -->')
    if login_start != -1 and user_info_start != -1:
        new_content = content[:login_start] + login_modal + content[user_info_start:]
    else:
        print(f"无法在{filename}中找到模态框标记")
        return False
    
    # 更新login()函数
    login_start = new_content.find('function login()')
    if login_start != -1:
        # 找到下一个函数开始或文件结束
        next_func_start = new_content.find('function ', login_start + 1)
        if next_func_start != -1:
            new_content = new_content[:login_start] + login_func + new_content[next_func_start:]
        else:
            new_content = new_content[:login_start] + login_func
    else:
        print(f"无法在{filename}中找到login()函数")
        return False
    
    # 保存文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

# 主函数
def main():
    print("获取标准登录组件...")
    login_modal, login_func = get_standard_components()
    print(f"登录模态框长度: {len(login_modal)} 字符")
    print(f"login()函数长度: {len(login_func)} 字符")
    
    # 要更新的HTML文件
    html_files = [
        'index.html', 'cases.html', 'experts.html', 
        'group.html', 'knowledge.html', 'news.html', 
        'services.html', 'about.html'
    ]
    
    # 更新所有文件
    for file in html_files:
        if os.path.exists(file):
            success = update_file(file, login_modal, login_func)
            if success:
                print(f"✓ {file} 更新成功")
            else:
                print(f"✗ {file} 更新失败")
        else:
            print(f"✗ {file} 文件不存在")
    
    print("\n所有文件更新完成！")

if __name__ == "__main__":
    main()