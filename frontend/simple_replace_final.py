# 简化版的登录模态框替换脚本

try:
    # 读取文件内容
    with open('cases.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找登录模态框的开始和结束标记
    login_start = content.find('<div class="modal fade" id="loginModal"')
    if login_start == -1:
        print("找不到登录模态框开始标签")
        exit(1)
    
    # 查找结束标签
    login_end = content.find('</div>', login_start)
    # 因为模态框有多层嵌套，我们需要找到正确的结束位置
    # 计算div标签的嵌套层数
    div_count = 0
    for i in range(login_start, content.length):
        if content[i:i+5] == '<div ':  # 开始标签
            div_count += 1
        elif content[i:i+6] == '</div>':  # 结束标签
            div_count -= 1
            if div_count == 0:
                login_end = i + 6
                break
    
    if login_end == -1:
        print("找不到登录模态框结束标签")
        exit(1)
    
    # 读取新的登录模态框内容
    with open('new_login_content.txt', 'r', encoding='utf-8') as f:
        new_login = f.read()
    
    # 构建新的内容
    new_content = content[:login_start] + new_login + content[login_end:]
    
    # 保存文件
    with open('cases.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("登录模态框替换成功！")
    
except Exception as e:
    print(f"发生错误：{e}")
    import traceback
    traceback.print_exc()
