#!/usr/bin/env python3
"""
统一所有HTML页面的登录/注册模态框脚本
"""
import os
import re

def main():
    # 读取模板文件
    template_path = "login_template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 提取登录/注册模态框的HTML代码
    login_modal_match = re.search(r'<!-- 登录模态框 -->.*?<!-- 用户信息模态框 -->.*?</div>', template_content, re.DOTALL)
    if not login_modal_match:
        print("无法从模板中提取登录模态框代码")
        return
    login_modal_html = login_modal_match.group(0)
    
    # 提取登录/注册功能的JavaScript代码
    js_match = re.search(r'<!-- 登录注册功能 JavaScript -->.*?</script>', template_content, re.DOTALL)
    if not js_match:
        print("无法从模板中提取JavaScript代码")
        return
    login_js = js_match.group(0)
    
    # 获取当前目录下的所有HTML文件
    html_files = [f for f in os.listdir('.') if f.endswith('.html') and f != template_path]
    
    for html_file in html_files:
        print(f"处理文件: {html_file}")
        
        # 读取文件内容
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除现有的登录/注册模态框
        # 匹配任何登录/注册相关的模态框
        content = re.sub(r'<!-- 登录模态框 -->.*?<!-- 用户信息模态框 -->.*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="modal fade" id="loginModal".*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="modal fade" id="registerModal".*?</div>', '', content, flags=re.DOTALL)
        content = re.sub(r'<div class="modal fade" id="userInfoModal".*?</div>', '', content, flags=re.DOTALL)
        
        # 移除现有的登录/注册相关的JavaScript代码
        content = re.sub(r'// 显示登录模态框.*?// 页面加载完成后检查登录状态.*?document\.addEventListener\(.*?\);', '', content, flags=re.DOTALL)
        content = re.sub(r'// 登录注册功能.*?document\.addEventListener\(.*?\);', '', content, flags=re.DOTALL)
        
        # 在body结束前添加统一的登录/注册模态框
        body_end = '</body>'
        if body_end in content:
            content = content.replace(body_end, f'{login_modal_html}\n{body_end}')
        
        # 在现有script标签前添加统一的JavaScript代码
        script_tags = re.findall(r'<script.*?</script>', content, re.DOTALL)
        if script_tags:
            last_script = script_tags[-1]
            content = content.replace(last_script, f'{login_js}\n{last_script}')
        else:
            # 如果没有script标签，在body结束前添加
            content = content.replace(body_end, f'{login_js}\n{body_end}')
        
        # 确保页面包含必要的jQuery和Bootstrap引用
        jquery_ref = '<script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.slim.min.js"></script>'
        bootstrap_ref = '<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>'
        
        if jquery_ref not in content:
            content = content.replace('</head>', f'{jquery_ref}\n{bootstrap_ref}\n</head>')
        
        # 保存修改后的文件
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"文件 {html_file} 处理完成")
    
    print("所有文件处理完成")

if __name__ == "__main__":
    main()