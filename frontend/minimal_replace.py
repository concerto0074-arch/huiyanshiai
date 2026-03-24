# 简单的登录模态框替换脚本

# 定义登录模态框的开始和结束标记
LOGIN_START = '<div class="modal fade" id="loginModal"'
REGISTER_START = '<!-- 注册模态框 -->'

# 定义新的登录模态框内容
NEW_LOGIN_MODAL = '''<div class="modal fade" id="loginModal" tabindex="-1" role="dialog" aria-labelledby="loginModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="loginModalLabel">登录</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <ul class="nav nav-tabs" id="loginTabs" role="tablist">
                        <li class="nav-item">
                            <a class="nav-link active" id="user-login-tab" data-toggle="tab" href="#user-login" role="tab" aria-controls="user-login" aria-selected="true">用户登录</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" id="admin-login-tab" data-toggle="tab" href="#admin-login" role="tab" aria-controls="admin-login" aria-selected="false">管理员登录</a>
                        </li>
                    </ul>
                    <div class="tab-content mt-3" id="loginTabsContent">
                        <div class="tab-pane fade show active" id="user-login" role="tabpanel" aria-labelledby="user-login-tab">
                            <form id="userLoginForm">
                                <div class="form-group">
                                    <label for="userLoginUsername">用户名</label>
                                    <input type="text" class="form-control" id="userLoginUsername" placeholder="请输入用户名" required>
                                </div>
                                <div class="form-group">
                                    <label for="userLoginPassword">密码</label>
                                    <input type="password" class="form-control" id="userLoginPassword" placeholder="请输入密码" required>
                                </div>
                                <div class="form-group form-check">
                                    <input type="checkbox" class="form-check-input" id="rememberMe">
                                    <label class="form-check-label" for="rememberMe">记住我</label>
                                </div>
                                <div id="loginError" class="text-danger" style="margin-bottom: 10px;"></div>
                            </form>
                        </div>
                        <div class="tab-pane fade" id="admin-login" role="tabpanel" aria-labelledby="admin-login-tab">
                            <form id="adminLoginForm">
                                <div class="form-group">
                                    <label for="adminLoginUsername">管理员用户名</label>
                                    <input type="text" class="form-control" id="adminLoginUsername" placeholder="请输入管理员用户名" required>
                                </div>
                                <div class="form-group">
                                    <label for="adminLoginPassword">管理员密码</label>
                                    <input type="password" class="form-control" id="adminLoginPassword" placeholder="请输入管理员密码" required>
                                </div>
                                <div id="adminLoginError" class="text-danger" style="margin-bottom: 10px;"></div>
                            </form>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">关闭</button>
                    <button type="button" class="btn btn-primary" onclick="login()">登录</button>
                    <button type="button" class="btn btn-link" onclick="showRegisterModal()">没有账号？立即注册</button>
                </div>
            </div>
        </div>
    </div>

    '''

# 执行替换
try:
    with open('cases.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到登录模态框的开始和结束位置
    start_pos = content.find(LOGIN_START)
    end_pos = content.find(REGISTER_START, start_pos)
    
    if start_pos == -1:
        print("错误：未找到登录模态框")
    elif end_pos == -1:
        print("错误：未找到注册模态框")
    else:
        # 构建新内容
        new_content = content[:start_pos] + NEW_LOGIN_MODAL + content[end_pos:]
        
        # 保存文件
        with open('cases.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("成功：登录模态框已更新为双选项卡版本")
        print(f"替换的字符数：{len(new_content) - len(content)}")
        
except Exception as e:
    print(f"错误：{str(e)}")