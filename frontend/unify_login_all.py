#!/usr/bin/env python3
import os
import re

# 获取products.html中的标准登录模态框和login()函数
def get_standard_login_components():
    print("正在读取products.html中的标准登录组件...")
    with open('products.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取登录模态框
    login_start = content.find('<!-- 登录模态框 -->')
    register_start = content.find('<!-- 注册模态框 -->')
    user_info_start = content.find('<!-- 用户信息模态框 -->')
    
    print(f"login_start: {login_start}, register_start: {register_start}, user_info_start: {user_info_start}")
    
    if login_start == -1 or register_start == -1 or user_info_start == -1:
        print("无法在products.html中找到完整的模态框组件")
        return None, None
    
    login_modal = content[login_start:user_info_start]
    print(f"提取的登录模态框长度: {len(login_modal)} 字符")
    
    # 提取login()函数
    login_func_match = re.search(r'function login\(\)[\s\S]*?^}', content, re.MULTILINE)
    if not login_func_match:
        print("无法在products.html中找到login()函数")
        return login_modal, None
    
    login_func = login_func_match.group(0)
    print(f"提取的login()函数长度: {len(login_func)} 字符")
    return login_modal, login_func

# 更新文件中的登录组件
def update_login_in_file(filename, login_modal, login_func):
    print(f"\n正在更新文件: {filename}")
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新登录模态框
    login_start = content.find('<!-- 登录模态框 -->')
    user_info_start = content.find('<!-- 用户信息模态框 -->')
    
    print(f"在{filename}中找到: login_start: {login_start}, user_info_start: {user_info_start}")
    
    if login_start == -1 or user_info_start == -1:
        print(f"无法在{filename}中找到完整的模态框组件")
        return False
    
    # 替换登录模态框
    new_content = content[:login_start] + login_modal + content[user_info_start:]
    print(f"替换登录模态框后内容长度: {len(new_content)} 字符")
    
    # 更新login()函数
    login_func_match = re.search(r'function login\(\)[\s\S]*?^}', new_content, re.MULTILINE)
    if not login_func_match:
        print(f"无法在{filename}中找到login()函数")
        return False
    
    new_content = new_content[:login_func_match.start()] + login_func + new_content[login_func_match.end():]
    print(f"替换login()函数后内容长度: {len(new_content)} 字符")
    
    # 保存更新后的内容
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"已成功更新{filename}")
    return True

# 主函数
def main():
    print("开始统一更新登录功能...")
    # 获取标准登录组件
    login_modal, login_func = get_standard_login_components()
    if not login_modal or not login_func:
        print("获取标准登录组件失败，程序终止")
        return
    
    # 要更新的HTML文件列表
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'admin_dashboard.html']
    print(f"找到的HTML文件: {html_files}")
    
    # 更新每个文件
    for file in html_files:
        update_login_in_file(file, login_modal, login_func)
    
    print("\n所有文件更新完成！")

if __name__ == "__main__":
    main()