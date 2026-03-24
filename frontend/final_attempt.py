# 最终尝试：使用简单的字符串替换方法

try:
    # 打开文件并读取内容
    with open('cases.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 定义要替换的部分内容（使用更短的标记）
    old_part = '<h5 class="modal-title" id="loginModalLabel">用户登录</h5>'
    new_part = '<h5 class="modal-title" id="loginModalLabel">登录</h5>\n                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">\n                        <span aria-hidden="true">&times;</span>\n                    </button>\n                </div>\n                <div class="modal-body">\n                    <!-- 登录选项卡 -->\n                    <ul class="nav nav-tabs" id="loginTabs" role="tablist">\n                        <li class="nav-item">\n                            <a class="nav-link active" id="user-login-tab" data-toggle="tab" href="#user-login" role="tab" aria-controls="user-login" aria-selected="true">用户登录</a>\n                        </li>\n                        <li class="nav-item">\n                            <a class="nav-link" id="admin-login-tab" data-toggle="tab" href="#admin-login" role="tab" aria-controls="admin-login" aria-selected="false">管理员登录</a>\n                        </li>\n                    </ul>\n                    <div class="tab-content mt-3" id="loginTabsContent">\n                        <!-- 用户登录表单 -->\n                        <div class="tab-pane fade show active" id="user-login" role="tabpanel" aria-labelledby="user-login-tab">\n                            <form id="userLoginForm">\n                                <div class="form-group">\n                                    <label for="userLoginUsername">用户名</label>\n                                    <input type="text" class="form-control" id="userLoginUsername" placeholder="请输入用户名" required>\n                                </div>\n                                <div class="form-group">\n                                    <label for="userLoginPassword">密码</label>\n                                    <input type="password" class="form-control" id="userLoginPassword" placeholder="请输入密码" required>\n                                </div>\n                                <div class="form-group form-check">\n                                    <input type="checkbox" class="form-check-input" id="rememberMe">\n                                    <label class="form-check-label" for="rememberMe">记住我</label>\n                                </div>\n                                <div id="loginError" class="text-danger" style="margin-bottom: 10px;"></div>\n                            </form>\n                        </div>\n                        <!-- 管理员登录表单 -->\n                        <div class="tab-pane fade" id="admin-login" role="tabpanel" aria-labelledby="admin-login-tab">\n                            <form id="adminLoginForm">\n                                <div class="form-group">\n                                    <label for="adminLoginUsername">管理员用户名</label>\n                                    <input type="text" class="form-control" id="adminLoginUsername" placeholder="请输入管理员用户名" required>\n                                </div>\n                                <div class="form-group">\n                                    <label for="adminLoginPassword">管理员密码</label>\n                                    <input type="password" class="form-control" id="adminLoginPassword" placeholder="请输入管理员密码" required>\n                                </div>\n                                <div id="adminLoginError" class="text-danger" style="margin-bottom: 10px;"></div>\n                            </form>\n                        </div>\n                    </div>\n                </div>\n                <div class="modal-footer">\n                    <button type="button" class="btn btn-secondary" data-dismiss="modal">关闭</button>\n                    <button type="button" class="btn btn-primary" onclick="login()">登录</button>\n                    <button type="button" class="btn btn-link" onclick="showRegisterModal()">没有账号？立即注册</button>\n                </div>'
    
    # 替换内容
    updated_content = content.replace(old_part, new_part)
    
    # 保存更新后的内容
    with open('cases.html', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("登录模态框已成功更新！")
    
except Exception as e:
    print(f"发生错误：{e}")
    import traceback
    traceback.print_exc()
