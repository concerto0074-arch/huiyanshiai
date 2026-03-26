/**
 * 慧眼识癌 - 全局统一认证模块
 * 包含登录、注册、登出功能，以及表单校验、密码强度检测、Toast 通知
 */

// ============================================================
// Toast 通知系统
// ============================================================

/**
 * 显示 Toast 通知
 * @param type 通知类型：'success' | 'error' | 'info'
 * @param message 通知内容
 * @param durationMs 持续时间（毫秒），默认 3500
 */
window.showToast = function(type, message, durationMs = 3500) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const iconMap = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        info: 'fas fa-info-circle'
    };

    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon"><i class="${iconMap[type] || iconMap.info}"></i></span>
        <span class="toast-msg">${message}</span>
        <span class="toast-close" onclick="this.parentElement.remove()">&times;</span>
    `;

    container.appendChild(toast);

    // NOTE: 使用 requestAnimationFrame 确保 CSS transition 正确触发
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });
    });

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, durationMs);
};

// ============================================================
// 密码可见性切换
// ============================================================

/**
 * 切换密码输入框的可见性
 * @param inputId 密码输入框 ID
 * @param iconId 切换图标的 ID
 */
window.togglePasswordVisibility = function(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!input || !icon) return;

    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    }
};

// ============================================================
// 表单实时校验逻辑
// ============================================================

/**
 * 检测密码强度
 * @param password 密码字符串
 * @returns 'weak' | 'medium' | 'strong'
 */
function checkPasswordStrength(password) {
    if (!password) return '';
    let score = 0;
    if (password.length >= 6) score++;
    if (password.length >= 10) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 2) return 'weak';
    if (score <= 3) return 'medium';
    return 'strong';
}

const STRENGTH_LABELS = {
    weak: '弱 — 建议使用更复杂的密码',
    medium: '中 — 可以接受',
    strong: '强 — 非常安全'
};

/**
 * 更新密码强度指示器 UI
 * @param password 当前输入的密码
 */
function updatePasswordStrengthUI(password) {
    const fill = document.getElementById('strengthFill');
    const text = document.getElementById('passwordStrengthText');
    if (!fill || !text) return;

    if (!password) {
        fill.className = 'strength-fill';
        text.textContent = '';
        text.className = 'password-strength-text';
        return;
    }

    const level = checkPasswordStrength(password);
    fill.className = `strength-fill ${level}`;
    text.textContent = STRENGTH_LABELS[level] || '';
    text.className = `password-strength-text ${level}`;
}

/**
 * 校验用户名格式：3-20 位，仅限字母、数字、下划线
 * @param username 用户名
 * @returns boolean
 */
function isValidUsername(username) {
    return /^[a-zA-Z0-9_]{3,20}$/.test(username);
}

/**
 * 校验邮箱格式
 * @param email 邮箱
 * @returns boolean
 */
function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * 校验手机号格式（中国大陆 11 位）
 * @param phone 手机号
 * @returns boolean
 */
function isValidPhone(phone) {
    if (!phone) return true; // 选填
    return /^1[3-9]\d{9}$/.test(phone);
}

// NOTE: 页面加载后为注册表单绑定实时校验事件
document.addEventListener('DOMContentLoaded', function() {
    const usernameInput = document.getElementById('registerUsername');
    const emailInput = document.getElementById('registerEmail');
    const phoneInput = document.getElementById('registerPhone');
    const passwordInput = document.getElementById('registerPassword');
    const confirmInput = document.getElementById('confirmPassword');

    if (usernameInput) {
        usernameInput.addEventListener('input', function() {
            const hint = document.getElementById('usernameHint');
            const val = this.value.trim();
            if (!val) {
                this.classList.remove('is-valid', 'is-invalid');
                if (hint) { hint.textContent = ''; hint.className = 'input-hint'; }
                return;
            }
            if (isValidUsername(val)) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (hint) { hint.textContent = '✓ 用户名格式正确'; hint.className = 'input-hint success'; }
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                if (hint) { hint.textContent = '仅限3-20位字母、数字或下划线'; hint.className = 'input-hint error'; }
            }
        });
    }

    if (emailInput) {
        emailInput.addEventListener('input', function() {
            const hint = document.getElementById('emailHint');
            const val = this.value.trim();
            if (!val) {
                this.classList.remove('is-valid', 'is-invalid');
                if (hint) { hint.textContent = ''; hint.className = 'input-hint'; }
                return;
            }
            if (isValidEmail(val)) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (hint) { hint.textContent = '✓ 邮箱格式正确'; hint.className = 'input-hint success'; }
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                if (hint) { hint.textContent = '请输入正确的邮箱地址'; hint.className = 'input-hint error'; }
            }
        });
    }

    if (phoneInput) {
        // NOTE: 限制只能输入数字
        phoneInput.addEventListener('input', function() {
            this.value = this.value.replace(/\D/g, '');
            const hint = document.getElementById('phoneHint');
            const val = this.value;
            if (!val) {
                this.classList.remove('is-valid', 'is-invalid');
                if (hint) { hint.textContent = ''; hint.className = 'input-hint'; }
                return;
            }
            if (isValidPhone(val)) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (hint) { hint.textContent = '✓ 手机号格式正确'; hint.className = 'input-hint success'; }
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
                if (hint) { hint.textContent = '请输入正确的11位手机号'; hint.className = 'input-hint error'; }
            }
        });
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            updatePasswordStrengthUI(this.value);
            // 密码变化时同步检查确认密码
            if (confirmInput && confirmInput.value) {
                validateConfirmPassword(confirmInput, this.value);
            }
        });
    }

    if (confirmInput) {
        confirmInput.addEventListener('input', function() {
            const pwdVal = passwordInput ? passwordInput.value : '';
            validateConfirmPassword(this, pwdVal);
        });
    }
});

/**
 * 校验确认密码是否一致
 * @param confirmEl 确认密码输入框元素
 * @param originalPassword 原始密码
 */
function validateConfirmPassword(confirmEl, originalPassword) {
    const hint = document.getElementById('confirmHint');
    const val = confirmEl.value;
    if (!val) {
        confirmEl.classList.remove('is-valid', 'is-invalid');
        if (hint) { hint.textContent = ''; hint.className = 'input-hint'; }
        return;
    }
    if (val === originalPassword) {
        confirmEl.classList.remove('is-invalid');
        confirmEl.classList.add('is-valid');
        if (hint) { hint.textContent = '✓ 密码一致'; hint.className = 'input-hint success'; }
    } else {
        confirmEl.classList.remove('is-valid');
        confirmEl.classList.add('is-invalid');
        if (hint) { hint.textContent = '两次输入的密码不一致'; hint.className = 'input-hint error'; }
    }
}

// ============================================================
// 注册功能
// ============================================================

/**
 * 切换注册按钮的 Loading 状态
 * @param isLoading 是否加载中
 */
function setRegisterLoading(isLoading) {
    const btn = document.getElementById('registerSubmitBtn');
    const textSpan = document.getElementById('registerBtnText');
    const spinnerSpan = document.getElementById('registerBtnSpinner');

    if (!btn) return;

    btn.disabled = isLoading;
    if (textSpan) textSpan.style.display = isLoading ? 'none' : 'inline';
    if (spinnerSpan) spinnerSpan.style.display = isLoading ? 'inline' : 'none';
}

window.register = async function() {
    const username = document.getElementById('registerUsername')?.value?.trim();
    const email = document.getElementById('registerEmail')?.value?.trim();
    const phone = document.getElementById('registerPhone')?.value?.trim() || '';
    const password = document.getElementById('registerPassword')?.value;
    const confirmPassword = document.getElementById('confirmPassword')?.value;
    const agreeTerms = document.getElementById('agreeTerms')?.checked;
    const errorDiv = document.getElementById('registerError');

    if (errorDiv) errorDiv.textContent = '';

    // ---- 前端校验 ----
    if (!username || !email || !password) {
        if (errorDiv) errorDiv.textContent = '请填写所有必填项（用户名、邮箱、密码）';
        return;
    }

    if (!isValidUsername(username)) {
        if (errorDiv) errorDiv.textContent = '用户名仅限3-20位字母、数字或下划线';
        return;
    }

    if (!isValidEmail(email)) {
        if (errorDiv) errorDiv.textContent = '请输入正确的邮箱地址';
        return;
    }

    if (phone && !isValidPhone(phone)) {
        if (errorDiv) errorDiv.textContent = '请输入正确的11位手机号';
        return;
    }

    if (password.length < 6) {
        if (errorDiv) errorDiv.textContent = '密码长度至少6位';
        return;
    }

    if (password !== confirmPassword) {
        if (errorDiv) errorDiv.textContent = '两次输入的密码不一致';
        return;
    }

    if (!agreeTerms) {
        if (errorDiv) errorDiv.textContent = '请先阅读并同意服务条款和隐私政策';
        return;
    }

    // ---- 发送注册请求 ----
    setRegisterLoading(true);

    try {
        const baseUrl = (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) ? window.APP_CONFIG.API_BASE_URL : '';
        const response = await fetch(`${baseUrl}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, phone })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            // 注册成功：关闭模态框 → 显示成功 Toast → 自动填充登录表单
            if ($('#registerModal').length) {
                $('#registerModal').modal('hide');
            }

            showToast('success', '🎉 注册成功！正在跳转到登录...');

            // NOTE: 注册成功后自动填充登录表单的用户名，减少用户操作
            setTimeout(() => {
                const loginUsernameInput = document.getElementById('userLoginUsername');
                if (loginUsernameInput) {
                    loginUsernameInput.value = username;
                }
                if (typeof showLoginModal === 'function') {
                    showLoginModal();
                }
            }, 1200);

            // 重置注册表单
            const form = document.getElementById('registerForm');
            if (form) form.reset();
            updatePasswordStrengthUI('');
            // 清除所有校验状态
            document.querySelectorAll('#registerForm .form-control').forEach(el => {
                el.classList.remove('is-valid', 'is-invalid');
            });
            document.querySelectorAll('#registerForm .input-hint').forEach(el => {
                el.textContent = '';
                el.className = 'input-hint';
            });
        } else {
            // 后端返回的错误信息
            const errMsg = data.error || '注册失败，请稍后重试';
            if (errorDiv) errorDiv.textContent = errMsg;
            showToast('error', errMsg);
        }
    } catch (error) {
        console.error('Register error:', error);
        const errMsg = '网络连接异常，请检查网络后重试';
        if (errorDiv) errorDiv.textContent = errMsg;
        showToast('error', errMsg);
    } finally {
        setRegisterLoading(false);
    }
};

// ============================================================
// 登录功能
// ============================================================

window.login = async function() {
    const activeTab = document.querySelector('#loginTabs .nav-link.active');
    let username, password, errorDiv, isAdminLogin = false;

    if (activeTab && activeTab.id === 'user-login-tab') {
        username = document.getElementById('userLoginUsername')?.value;
        password = document.getElementById('userLoginPassword')?.value;
        errorDiv = document.getElementById('loginError');
    } else if (activeTab && activeTab.id === 'admin-login-tab') {
        username = document.getElementById('adminLoginUsername')?.value;
        password = document.getElementById('adminLoginPassword')?.value;
        errorDiv = document.getElementById('adminLoginError');
        isAdminLogin = true;
    } else {
        username = document.getElementById('userLoginUsername')?.value || document.getElementById('loginUsername')?.value;
        password = document.getElementById('userLoginPassword')?.value || document.getElementById('loginPassword')?.value;
        errorDiv = document.getElementById('loginError') || document.getElementById('adminLoginError');

        // HACK: 兼容管理员登录页面独立表单
        if(document.getElementById('adminLoginUsername') && document.getElementById('adminLoginUsername').value) {
           username = document.getElementById('adminLoginUsername').value;
           password = document.getElementById('adminLoginPassword').value;
           isAdminLogin = true;
        }
    }

    if (errorDiv) errorDiv.textContent = '';

    if (!username || !password) {
        if (errorDiv) errorDiv.textContent = '请输入用户名和密码';
        if (!errorDiv) showToast('error', '请输入用户名和密码');
        return;
    }

    try {
        const baseUrl = (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL) ? window.APP_CONFIG.API_BASE_URL : '';
        const response = await fetch(`${baseUrl}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('username', data.user.username);
            localStorage.setItem('email', data.user.email);
            localStorage.setItem('role', data.user.role);
            localStorage.setItem('token', data.token);

            if (data.user.role === 'admin') {
                localStorage.setItem('adminLoggedIn', 'true');
                localStorage.setItem('X-Admin-Token', data.token);
            }

            if ($('#loginModal').length) {
                $('#loginModal').modal('hide');
            }

            showToast('success', isAdminLogin ? '✅ 管理员登录成功！' : '✅ 登录成功！');

            setTimeout(() => {
                if (isAdminLogin || data.user.role === 'admin') {
                    if (window.location.href.includes('admin_dashboard.html')) {
                        window.location.reload();
                    } else {
                        window.location.href = 'admin_dashboard.html';
                    }
                } else {
                    if (!window.location.href.includes('user_center.html')) {
                        window.location.href = 'user_center.html';
                    } else {
                        window.location.reload();
                    }
                }
            }, 800);
        } else {
            const errMsg = data.error || '登录失败，请检查用户名和密码';
            if (errorDiv) errorDiv.textContent = errMsg;
            else showToast('error', errMsg);
        }
    } catch (error) {
        console.error('Login error:', error);
        const errMsg = '网络连接异常，请稍后重试';
        if (errorDiv) errorDiv.textContent = errMsg;
        else showToast('error', errMsg);
    }
};

// ============================================================
// 登出功能
// ============================================================

window.logout = function() {
    localStorage.removeItem('adminLoggedIn');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('username');
    localStorage.removeItem('email');
    localStorage.removeItem('role');
    localStorage.removeItem('token');
    localStorage.removeItem('X-Admin-Token');
    showToast('info', '已安全退出登录');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 800);
};
