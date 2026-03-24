# 更新login.js函数以支持管理员登录

try:
    # 读取cases.html文件内容
    with open('cases.html', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 找到当前的login函数
    old_login_function = '''        // 用户登录
        function login() {
            var username = document.getElementById('loginUsername').value;
            var password = document.getElementById('loginPassword').value;
            var rememberMe = document.getElementById('rememberMe').checked;
            
            // 发送登录请求
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    remember_me: rememberMe
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 登录成功
                    alert('登录成功！');
                    $('#loginModal').modal('hide');
                    updateUserInfo(data.username, data.is_admin);
                } else {
                    // 登录失败
                    document.getElementById('loginError').innerText = data.message;
                }
            })
            .catch(error => {
                console.error('登录失败:', error);
                document.getElementById('loginError').innerText = '登录失败，请重试。';
            });
        }'''
    
    # 定义新的login函数
    new_login_function = '''        // 用户登录
        function login() {
            // 获取当前激活的标签页
            var activeTab = $('#loginTabs .nav-link.active').attr('id');
            var username, password;
            
            if (activeTab === 'user-login-tab') {
                // 用户登录
                username = document.getElementById('userLoginUsername').value;
                password = document.getElementById('userLoginPassword').value;
            } else {
                // 管理员登录
                username = document.getElementById('adminLoginUsername').value;
                password = document.getElementById('adminLoginPassword').value;
            }
            
            var rememberMe = document.getElementById('rememberMe') ? document.getElementById('rememberMe').checked : false;
            
            // 发送登录请求
            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    remember_me: rememberMe
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 登录成功
                    alert('登录成功！');
                    $('#loginModal').modal('hide');
                    updateUserInfo(data.username, data.is_admin);
                } else {
                    // 登录失败
                    if (activeTab === 'user-login-tab') {
                        document.getElementById('loginError').innerText = data.message;
                    } else {
                        document.getElementById('adminLoginError').innerText = data.message;
                    }
                }
            })
            .catch(error => {
                console.error('登录失败:', error);
                if (activeTab === 'user-login-tab') {
                    document.getElementById('loginError').innerText = '登录失败，请重试。';
                } else {
                    document.getElementById('adminLoginError').innerText = '登录失败，请重试。';
                }
            });
        }'''
    
    # 替换login函数
    updated_content = content.replace(old_login_function, new_login_function)
    
    # 保存更新后的内容
    with open('cases.html', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print("login函数已成功更新！")
    
except Exception as e:
    print(f"发生错误：{e}")
    import traceback
    traceback.print_exc()
