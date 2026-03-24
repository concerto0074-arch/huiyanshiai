# 读取原始文件内容
with open('cases.html', 'r', encoding='utf-8') as file:
    content = file.read()

# 定义要替换的旧登录模态框内容
old_login = '''    <!-- 登录模态框 -->
    <div class="modal fade" id="loginModal" tabindex="-1" role="dialog" aria-labelledby="loginModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="loginModalLabel">用户登录</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="loginUsername">用户名</label>
                            <input type="text" class="form-control" id="loginUsername" placeholder="请输入用户名" required>
                        </div>
                        <div class="form-group">
                            <label for="loginPassword">密码</label>
                            <input type="password" class="form-control" id="loginPassword" placeholder="请输入密码" required>
                        </div>
                        <div class="form-group form-check">
                            <input type="checkbox" class="form-check-input" id="rememberMe">
                            <label class="form-check-label" for="rememberMe">记住我</label>
                        </div>
                        <div id="loginError" class="text-danger" style="margin-bottom: 10px;"></div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-dismiss="modal">关闭</button>
                    <button type="button" class="btn btn-primary" onclick="login()">登录</button>
                    <button type="button" class="btn btn-link" onclick="showRegisterModal()">没有账号？立即注册</button>
                </div>
            </div>
        </div>
    </div>'''

# 定义新的登录模态框内容（包含用户和管理员选项卡）
new_login = '''    <!-- 登录模态框 -->
    <div class="modal fade" id="loginModal" tabindex="-1" role="dialog" aria-labelledby="loginModalLabel" aria-hidden="true">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="loginModalLabel">登录</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body">
                    <!-- 登录选项卡 -->
                    <ul class="nav nav-tabs" id="loginTabs" role="tablist">
                        <li class="nav-item">
                            <a class="nav-link active" id="user-login-tab" data-toggle="tab" href="#user-login" role="tab" aria-controls="user-login" aria-selected="true">用户登录</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" id="admin-login-tab" data-toggle="tab" href="#admin-login" role="tab" aria-controls="admin-login" aria-selected="false">管理员登录</a>
                        </li>
                    </ul>
                    <div class="tab-content mt-3" id="loginTabsContent">
                        <!-- 用户登录表单 -->
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
                        <!-- 管理员登录表单 -->
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
    </div>'''

# 替换内容
updated_content = content.replace(old_login, new_login)

# 保存修改后的内容
with open('cases.html', 'w', encoding='utf-8') as file:
    file.write(updated_content)

print("登录模态框已成功更新！")
