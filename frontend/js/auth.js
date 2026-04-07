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
// 全站统一：登录/注册弹窗打开方法
// ============================================================

function openBootstrapModal(modalId) {
    try {
        if (window.jQuery && typeof window.jQuery === 'function') {
            const $ = window.jQuery;
            const el = $(modalId);
            if (el && el.length) {
                el.modal('show');
                return true;
            }
        }
    } catch (_) {
        // ignore
    }
    return false;
}

// 监听 modal 可见性变化（class="show"），一旦显示立即统一结构
function watchModalVisibility(modalEl) {
    try {
        if (!modalEl || modalEl.__visibilityObserved) return;
        const obs = new MutationObserver(() => {
            const isShown = modalEl.classList.contains('show');
            if (isShown) {
                if (modalEl.id === 'registerModal') {
                    try {
                        normalizeRegisterModalStructure();
                        normalizeRegisterAgreement();
                        bindPolicyLinks();
                    } catch (_) {}
                } else if (modalEl.id === 'loginModal') {
                    try { normalizeLoginModalStructure(); } catch (_) {}
                }
                // 无论哪种触发方式，始终应用内联样式
                try { injectSharedAuthStyles(); applyModalInlineStyles(modalEl.id); } catch (_) {}
            }
        });
        obs.observe(modalEl, { attributes: true, attributeFilter: ['class'] });
        modalEl.__visibilityObserved = true;
    } catch (_) {}
}

// 捕获所有 data-target / href 指向 modal 的点击，提前安排一次统一
function attachDelegatedOpeners() {
    if (window.__authDelegatedClicks) return;
    window.__authDelegatedClicks = true;
    document.addEventListener('click', function(e) {
        try {
            const path = e.composedPath ? e.composedPath() : (function build(n){const a=[];while(n){a.push(n);n=n.parentNode;}return a;})(e.target);
            let targetEl = null;
            for (const el of path) {
                if (!(el instanceof HTMLElement)) continue;
                const t = el.getAttribute && (el.getAttribute('data-target') || el.getAttribute('href'));
                if (t === '#registerModal' || t === '#loginModal') { targetEl = el; break; }
            }
            if (!targetEl) return;
            setTimeout(() => {
                try {
                    normalizeLoginModalStructure();
                    normalizeRegisterModalStructure();
                    normalizeRegisterAgreement();
                    bindPolicyLinks();
                } catch (_) {}
            }, 0);
        } catch (_) {}
    }, true);
}

// 监听 Bootstrap 弹窗打开事件，保证每次打开时都应用统一结构
function attachModalNormalization() {
    if (window.__authModalEventsBound) return;
    window.__authModalEventsBound = true;

    try {
        if (window.jQuery && typeof window.jQuery === 'function') {
            const $ = window.jQuery;
            $(document).on('show.bs.modal', '#registerModal', function() {
                try {
                    normalizeRegisterModalStructure();
                    normalizeRegisterAgreement();
                    bindPolicyLinks();
                } catch (_) {}
            });
            $(document).on('show.bs.modal', '#loginModal', function() {
                try {
                    normalizeLoginModalStructure();
                } catch (_) {}
            });
        }
    } catch (_) {
        // ignore
    }
}

// 监听 DOM 变更，处理后插入的旧版 modal 结构
function observeAddedModals() {
    if (!('MutationObserver' in window)) return;
    if (window.__authModalObserver) return;

    const observer = new MutationObserver((mutations) => {
        for (const m of mutations) {
            for (const node of m.addedNodes) {
                if (!(node instanceof HTMLElement)) continue;
                const reg = node.id === 'registerModal' ? node : node.querySelector && node.querySelector('#registerModal');
                const log = node.id === 'loginModal' ? node : node.querySelector && node.querySelector('#loginModal');
                if (reg) {
                    try {
                        normalizeRegisterModalStructure();
                        normalizeRegisterAgreement();
                        bindPolicyLinks();
                        watchModalVisibility(reg);
                    } catch (_) {}
                }
                if (log) {
                    try {
                        normalizeLoginModalStructure();
                        watchModalVisibility(log);
                    } catch (_) {}
                }
            }
        }
    });
    observer.observe(document.body || document.documentElement, { childList: true, subtree: true });
    window.__authModalObserver = observer;
}

function closeBootstrapModal(modalId) {
    try {
        if (window.jQuery && typeof window.jQuery === 'function') {
            const $ = window.jQuery;
            const el = $(modalId);
            if (el && el.length) {
                el.modal('hide');
                return true;
            }
        }
    } catch (_) {
        // ignore
    }
    return false;
}

function redirectToIndexWithAuth(action) {
    try {
        const url = new URL(window.location.href);
        url.pathname = url.pathname.replace(/[^/]*$/, 'index.html');
        url.searchParams.set('auth', action);
        window.location.href = url.toString();
    } catch (_) {
        window.location.href = `index.html?auth=${encodeURIComponent(action)}`;
    }
}

function applyModalInlineStyles(modalId) {
    try {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        const dialog = modal.querySelector('.modal-dialog');
        if (dialog) {
            dialog.style.maxWidth = '580px';
            dialog.style.width = '92vw';
            dialog.style.margin = '1.5rem auto';
        }
        const content = modal.querySelector('.modal-content');
        const header = modal.querySelector('.modal-header');
        const body = modal.querySelector('.modal-body');
        const footer = modal.querySelector('.modal-footer');
        const title = modal.querySelector('.modal-title');
        if (content) {
            content.style.cssText = 'display:flex;flex-direction:column;max-height:calc(100vh - 80px);overflow:hidden;border-radius:28px;border:1px solid rgba(255,255,255,0.4);box-shadow:0 40px 100px rgba(0,0,0,0.2);background:rgba(255,255,255,0.95);';
        }
        if (header) {
            header.style.cssText = 'background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#fff;padding:18px 28px;border-bottom:none;flex-shrink:0;display:flex;align-items:center;justify-content:space-between;border-radius:28px 28px 0 0;';
        }
        if (title) title.style.cssText = 'color:#fff;font-weight:800;font-size:1.3rem;margin:0;';
        const closeBtn = header && header.querySelector('.close');
        if (closeBtn) closeBtn.style.cssText = 'color:#fff;opacity:0.85;text-shadow:none;font-size:1.4rem;';
        if (body) {
            body.style.cssText = 'flex:1 1 auto;overflow-y:auto;overflow-x:hidden;padding:16px 28px 8px;min-height:0;';
        }
        if (footer) {
            footer.style.cssText = 'flex-shrink:0;padding:8px 28px 20px;border-top:none;background:transparent;';
        }
    } catch(_) {}
}

window.__authUnifiedShowLoginModal = function() {
    try {
        injectSharedAuthStyles();
        normalizeLoginModalStructure();
        applyModalInlineStyles('loginModal');
    } catch (_) {}
    closeBootstrapModal('#registerModal');
    if (!openBootstrapModal('#loginModal')) {
        redirectToIndexWithAuth('login');
    }
};

window.__authUnifiedShowRegisterModal = function() {
    try {
        injectSharedAuthStyles();
        normalizeRegisterModalStructure();
        normalizeRegisterAgreement();
        bindPolicyLinks();
        applyModalInlineStyles('registerModal');
    } catch (_) {}
    closeBootstrapModal('#loginModal');
    if (!openBootstrapModal('#registerModal')) {
        redirectToIndexWithAuth('register');
    }
};

function injectSharedAuthStyles() {
    const existing = document.getElementById('sharedAuthStyle');
    if (existing) existing.remove();
    const style = document.createElement('style');
    style.id = 'sharedAuthStyle';
    style.textContent = `
        /* 增强型毛玻璃认证弹窗样式 */
        #loginModal .modal-dialog, #registerModal .modal-dialog {
            max-width: 560px !important;
            margin: 1.5rem auto !important;
        }
        #loginModal .modal-content, #registerModal .modal-content {
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            border-radius: 28px !important;
            overflow: hidden !important;
            box-shadow: 0 40px 100px rgba(0, 0, 0, 0.2) !important;
            backdrop-filter: blur(20px) saturate(160%) !important;
            background: rgba(255, 255, 255, 0.95) !important;
            display: flex !important;
            flex-direction: column !important;
            max-height: calc(100vh - 3.5rem) !important;
        }
        #loginModal .modal-header, #registerModal .modal-header {
            flex-shrink: 0 !important;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
            color: #ffffff !important;
            border-bottom: none !important;
            padding: 18px 28px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            border-radius: 28px 28px 0 0 !important;
        }
        #loginModal .modal-title, #registerModal .modal-title {
            color: #ffffff !important;
            font-weight: 800 !important;
            font-size: 1.5rem !important;
            letter-spacing: -0.02em !important;
        }
        #loginModal .close, #registerModal .close {
            color: #ffffff;
            opacity: 0.8;
            text-shadow: none;
            transition: all 0.2s;
            outline: none;
        }
        #loginModal .close:hover, #registerModal .close:hover {
            opacity: 1;
            transform: scale(1.1);
        }
        #loginModal .modal-body, #registerModal .modal-body {
            padding: 24px 32px 16px;
            flex: 1 1 auto !important;
            overflow-y: auto !important;
            overflow-x: hidden !important;
        }
        #loginModal .modal-footer, #registerModal .modal-footer {
            padding: 16px 32px 28px !important;
            border-top: none !important;
            background: transparent !important;
            flex-shrink: 0 !important;
        }

        /* Tabs 胶囊式设计 */
        .auth-premium-tabs {
            background: rgba(15, 23, 42, 0.05);
            padding: 4px;
            border-radius: 14px;
            display: flex !important;
            border: none !important;
            margin-bottom: 24px;
        }
        .auth-premium-tabs .nav-item {
            flex: 1;
            margin: 0;
            list-style: none !important;
        }
        .auth-premium-tabs .nav-link {
            border: none !important;
            border-radius: 11px !important;
            padding: 10px 15px !important;
            font-weight: 700;
            color: #64748b !important;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: transparent !important;
            margin: 0 !important;
            font-size: 0.95rem;
        }
        .auth-premium-tabs .nav-link.active {
            background: #ffffff !important;
            color: #2563eb !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        /* 表单输入框优化 */
        .auth-field-label {
            font-weight: 700;
            color: #1e293b;
            font-size: 0.88rem;
            margin-bottom: 8px;
            display: block;
        }
        .auth-input-container {
            position: relative;
            margin-bottom: 10px;
        }
        .auth-input-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-size: 1rem;
            transition: color 0.3s;
            z-index: 5;
        }
        .auth-input-premium {
            padding-left: 42px !important;
            height: 44px !important;
            border-radius: 12px !important;
            border: 2px solid #f1f5f9 !important;
            background: #f8fafc !important;
            font-weight: 500;
            transition: all 0.3s;
        }
        .auth-input-premium:focus {
            border-color: #3b82f6 !important;
            background: #ffffff !important;
            box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1) !important;
        }
        .auth-input-premium:focus + .auth-input-icon {
            color: #3b82f6;
        }

        /* 渐变按钮 */
        .auth-btn-gradient {
            height: 52px;
            border-radius: 14px;
            font-weight: 800;
            font-size: 1.05rem;
            letter-spacing: 0.01em;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            border: none;
            color: white;
            transition: all 0.3s;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.25);
        }
        .auth-btn-gradient:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 25px rgba(37, 99, 235, 0.35);
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }
        .auth-btn-gradient:active {
            transform: translateY(0);
        }

        /* 切换链接 */
        .auth-footer-links {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin-top: 12px;
            font-size: 0.88rem;
            color: #64748b;
        }
        .auth-link-premium {
            color: #2563eb;
            font-weight: 700;
            text-decoration: none;
            transition: color 0.2s;
        }
        .auth-link-premium:hover {
            color: #1d4ed8;
            text-decoration: underline;
        }

        /* 密码强度条 */
        .password-strength-bar {
            height: 6px;
            background: #f1f5f9;
            border-radius: 3px;
            margin: 8px 0;
            overflow: hidden;
        }
        .strength-fill {
            height: 100%;
            width: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .strength-fill.weak { width: 33%; background: #ef4444; }
        .strength-fill.medium { width: 66%; background: #f59e0b; }
        .strength-fill.strong { width: 100%; background: #10b981; }

        .auth-helper-text { font-size: 0.78rem; color: #94a3b8; display: block; margin-top: 4px; }
        .input-hint { font-size: 0.78rem; height: 18px; margin-top: 4px; }
        .input-hint.success { color: #10b981; }
        .input-hint.error { color: #ef4444; }

        /* 密码输入框+眼睛图标 */
        .auth-password-wrap {
            position: relative;
            display: block;
            width: 100%;
        }
        .auth-input-container > .auth-password-wrap {
            padding-left: 0;
        }
        .auth-password-wrap .auth-input-premium {
            padding-right: 44px !important;
        }
        .toggle-password {
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            color: #94a3b8;
            font-size: 0.95rem;
            z-index: 10;
            transition: color 0.2s;
        }
        .toggle-password:hover { color: #3b82f6; }

        /* 服务协议图标修复 */
        .agreement-notice-icon {
            width: 26px !important;
            height: 26px !important;
            border-radius: 8px !important;
            font-size: 0.85rem !important;
        }

        .agreement-notice {
            margin-top: 12px;
            padding: 14px 16px;
            border-radius: 12px;
            background: #f8fbff;
            border: 1px solid rgba(191, 219, 254, 0.9);
            box-shadow: none;
        }
        .agreement-notice-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }
        .agreement-notice-icon {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #1d4ed8;
            background: rgba(219, 234, 254, 0.9);
            box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.14);
            flex-shrink: 0;
        }
        .agreement-notice-title {
            margin: 0;
            font-size: 0.95rem;
            font-weight: 700;
            color: #1e3a8a;
        }
        .agreement-notice-subtitle {
            margin: 2px 0 0;
            font-size: 0.8rem;
            color: #64748b;
            line-height: 1.55;
        }
        .agreement-notice .agree-terms {
            display: block;
            margin: 0;
        }
        .agreement-notice .agree-terms label {
            margin: 0;
            font-size: 0.88rem;
            color: #334155;
            line-height: 1.75;
            display: block;
        }
        .agreement-link {
            color: #2563eb;
            font-weight: 600;
            text-decoration: none;
            border-bottom: 1px dashed rgba(37, 99, 235, 0.35);
            transition: all 0.2s ease;
        }
        .agreement-link:hover {
            color: #1d4ed8;
            text-decoration: none;
            border-bottom-color: rgba(29, 78, 216, 0.75);
        }
        .agreement-footnote {
            margin-top: 8px;
            padding-left: 44px;
            font-size: 0.76rem;
            color: #64748b;
            line-height: 1.65;
        }
        .policy-modal .modal-header {
            background: linear-gradient(135deg, #eff6ff 0%, #f8fbff 100%);
            border-bottom: 1px solid #dbeafe;
        }
        .policy-modal .modal-title {
            color: #1e3a8a;
            font-weight: 800;
        }
        .policy-modal .modal-body {
            max-height: 70vh;
            overflow-y: auto;
            padding: 26px 28px;
        }
        .policy-section {
            margin-bottom: 18px;
            padding: 16px 18px;
            background: #f8fafc;
            border-radius: 12px;
            border-left: 4px solid #60a5fa;
        }
        .policy-section h6 {
            margin-bottom: 8px;
            font-weight: 800;
            color: #1e3a8a;
        }
        .policy-section p, .policy-section li {
            color: #475569;
            line-height: 1.8;
            font-size: 0.95rem;
        }
        .policy-section ul {
            margin-bottom: 0;
            padding-left: 20px;
        }
    `;
    document.head.appendChild(style);
}

function ensurePolicyModals() {
    if (document.getElementById('serviceAgreementModal')) return;
    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
    <div class="modal fade policy-modal" id="serviceAgreementModal" tabindex="-1" role="dialog" aria-labelledby="serviceAgreementModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="serviceAgreementModalLabel"><i class="fas fa-file-contract mr-2"></i>平台用户服务协议</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                </div>
                <div class="modal-body">
                    <div class="policy-section"><h6>一、服务定位</h6><p>慧眼识癌平台聚焦基层普惠型癌症早筛与健康风险评估服务，为用户提供智能化风险分析、健康报告生成、筛查辅助建议及相关信息服务。</p></div>
                    <div class="policy-section"><h6>二、用户账户</h6><ul><li>用户应提供真实、完整、可联系的注册信息。</li><li>用户应妥善保管账户及密码，不得将账户用于任何违法违规用途。</li><li>因账户保管不当造成的损失，平台将在合理范围内协助处理。</li></ul></div>
                    <div class="policy-section"><h6>三、服务边界</h6><p>平台输出的风险评估结果、算法分析与健康建议仅作为辅助参考，不能替代执业医师的面诊、诊断或治疗意见。若存在异常结果或身体不适，请及时前往正规医疗机构就诊。</p></div>
                    <div class="policy-section"><h6>四、平台责任</h6><p>平台将持续优化模型性能、系统稳定性与信息安全保障机制，并在适用范围内为用户提供更加清晰、透明、可信赖的健康服务体验。</p></div>
                </div>
                <div class="modal-footer"><button type="button" class="btn btn-primary" data-dismiss="modal">我已了解</button></div>
            </div>
        </div>
    </div>
    <div class="modal fade policy-modal" id="privacyPolicyModal" tabindex="-1" role="dialog" aria-labelledby="privacyPolicyModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="privacyPolicyModalLabel"><i class="fas fa-user-shield mr-2"></i>隐私保护政策</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                </div>
                <div class="modal-body">
                    <div class="policy-section"><h6>一、信息收集范围</h6><p>为完成注册、登录、报告生成与服务通知，平台可能收集您的账户信息、联系方式、上传的健康相关数据及必要的操作日志。</p></div>
                    <div class="policy-section"><h6>二、信息使用原则</h6><ul><li>仅用于账户认证、健康报告生成、服务通知与平台功能优化。</li><li>遵循最小必要原则，不超范围采集、不超目的使用。</li><li>未经用户授权或法律法规要求，不向无关第三方披露个人信息。</li></ul></div>
                    <div class="policy-section"><h6>三、安全保护措施</h6><p>平台采用访问控制、数据隔离、传输保护及日志审计等安全措施，尽力保障用户个人信息与医疗健康相关数据的安全性与完整性。</p></div>
                    <div class="policy-section"><h6>四、用户权利</h6><p>您有权查询、更正、更新与管理您的账户信息。如您对信息处理方式有疑问，可通过平台后续开放的客服与反馈渠道联系我们。</p></div>
                </div>
                <div class="modal-footer"><button type="button" class="btn btn-primary" data-dismiss="modal">我已了解</button></div>
            </div>
        </div>
    </div>
    <div class="modal fade policy-modal" id="medicalInfoModal" tabindex="-1" role="dialog" aria-labelledby="medicalInfoModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="medicalInfoModalLabel"><i class="fas fa-notes-medical mr-2"></i>医疗信息使用说明</h5>
                    <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                </div>
                <div class="modal-body">
                    <div class="policy-section"><h6>一、使用目的</h6><p>用户提交的健康相关信息主要用于模型推理、风险评估、报告生成、结果展示及相关健康服务支持，不用于与平台核心服务无关的商业用途。</p></div>
                    <div class="policy-section"><h6>二、数据类型说明</h6><ul><li>基础信息：如年龄、性别、联系方式等。</li><li>健康数据：如检测指标、影像特征、问卷信息、上传文件等。</li><li>系统信息：如访问日志、操作记录与错误排查信息。</li></ul></div>
                    <div class="policy-section"><h6>三、特别提醒</h6><p>平台服务适用于健康管理与早筛辅助场景，评估结果不构成临床诊断依据。涉及诊疗决策时，请务必以具备资质的医疗机构及医生意见为准。</p></div>
                    <div class="policy-section"><h6>四、持续优化</h6><p>为提升基层普惠型健康服务能力，平台可能基于脱敏、去标识化或统计分析方式对服务数据进行模型优化与产品改进，前提是符合相关法律法规及信息保护要求。</p></div>
                </div>
                <div class="modal-footer"><button type="button" class="btn btn-primary" data-dismiss="modal">我已了解</button></div>
            </div>
        </div>
    </div>`;
    document.body.appendChild(wrapper);
}

function buildAgreementNotice() {
    const wrapper = document.createElement('div');
    wrapper.className = 'agreement-notice';
    wrapper.innerHTML = `
        <div class="agreement-notice-header">
            <div class="agreement-notice-icon"><i class="fas fa-shield-alt"></i></div>
            <div>
                <p class="agreement-notice-title">医疗健康信息合规提示</p>
                <p class="agreement-notice-subtitle">为便于你了解平台边界与数据使用方式，下方提供用户协议、隐私政策与医疗信息使用说明入口。</p>
            </div>
        </div>
        <div class="agree-terms">
            <label>注册即表示你可以随时查看 <a href="#" class="agreement-link" data-policy="service">《平台用户服务协议》</a>、<a href="#" class="agreement-link" data-policy="privacy">《隐私保护政策》</a> 及 <a href="#" class="agreement-link" data-policy="medical">《医疗信息使用说明》</a></label>
        </div>
        <div class="agreement-footnote">本平台提供的结果用于健康管理与早筛辅助参考，不替代医生面诊、诊断或治疗意见。</div>
    `;
    return wrapper;
}

function removeRegisterPlanSections() {
    const registerModal = document.getElementById('registerModal');
    if (!registerModal) return;

    const registerPlan = registerModal.querySelector('#registerPlan');
    if (registerPlan) {
        const group = registerPlan.closest('.form-group');
        if (group) group.remove();
        else registerPlan.remove();
    }

    registerModal.querySelectorAll('.plan-cards').forEach(el => {
        const group = el.closest('.form-group');
        if (group) group.remove();
        else el.remove();
    });

    registerModal.querySelectorAll('.plan-card').forEach(el => {
        const group = el.closest('.form-group');
        if (group) group.remove();
        else el.remove();
    });

    registerModal.querySelectorAll('label').forEach(label => {
        const text = (label.textContent || '').replace(/\s+/g, ' ').trim();
        if (text.includes('选择套餐')) {
            const group = label.closest('.form-group');
            if (group) group.remove();
        }
    });
}

function buildUnifiedRegisterFormMarkup() {
    return `
        <form id="registerForm" novalidate>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px 16px;">
                <div class="form-group mb-0">
                    <label class="auth-field-label" for="registerUsername">用户名 <span class="text-danger">*</span></label>
                    <div class="auth-input-container" style="margin-bottom:4px;">
                        <i class="fas fa-user auth-input-icon"></i>
                        <input type="text" class="form-control auth-input-premium" id="registerUsername" placeholder="3-20位字符" required minlength="3" maxlength="20" autocomplete="username">
                    </div>
                    <div class="input-hint" id="usernameHint" style="font-size:0.75rem;min-height:16px;"></div>
                </div>
                <div class="form-group mb-0">
                    <label class="auth-field-label" for="registerEmail">邮箱地址 <span class="text-danger">*</span></label>
                    <div class="auth-input-container" style="margin-bottom:4px;">
                        <i class="fas fa-envelope auth-input-icon"></i>
                        <input type="email" class="form-control auth-input-premium" id="registerEmail" placeholder="example@email.com" required autocomplete="email">
                    </div>
                    <div class="input-hint" id="emailHint" style="font-size:0.75rem;min-height:16px;"></div>
                </div>
                <div class="form-group mb-0">
                    <label class="auth-field-label" for="registerPhone">手机号 <small class="text-muted">（可选）</small></label>
                    <div class="auth-input-container" style="margin-bottom:4px;">
                        <i class="fas fa-mobile-alt auth-input-icon"></i>
                        <input type="tel" class="form-control auth-input-premium" id="registerPhone" placeholder="11位手机号码" maxlength="11" autocomplete="tel">
                    </div>
                    <div class="input-hint" id="phoneHint" style="font-size:0.75rem;min-height:16px;"></div>
                </div>
                <div class="form-group mb-0">
                    <label class="auth-field-label" for="registerPassword">创建密码 <span class="text-danger">*</span></label>
                    <div class="auth-input-container" style="margin-bottom:4px;">
                        <i class="fas fa-lock auth-input-icon"></i>
                        <div class="auth-password-wrap">
                            <input type="password" class="form-control auth-input-premium" id="registerPassword" placeholder="8位以上字母数字" required minlength="8" maxlength="20" autocomplete="new-password">
                            <i class="fas fa-eye-slash toggle-password" id="toggleRegPassword" onclick="togglePasswordVisibility('registerPassword', 'toggleRegPassword')"></i>
                        </div>
                    </div>
                    <div class="password-strength-bar" id="passwordStrengthBar" style="margin:2px 0;"><div class="strength-fill" id="strengthFill"></div></div>
                </div>
                <div class="form-group mb-0" style="grid-column:1/-1;">
                    <label class="auth-field-label" for="confirmPassword">确认密码 <span class="text-danger">*</span></label>
                    <div class="auth-input-container" style="margin-bottom:4px;">
                        <i class="fas fa-shield-alt auth-input-icon"></i>
                        <div class="auth-password-wrap">
                            <input type="password" class="form-control auth-input-premium" id="confirmPassword" placeholder="再次输入密码" required autocomplete="new-password">
                            <i class="fas fa-eye-slash toggle-password" id="toggleConfirmPassword" onclick="togglePasswordVisibility('confirmPassword', 'toggleConfirmPassword')"></i>
                        </div>
                    </div>
                    <div class="input-hint" id="confirmHint" style="font-size:0.75rem;min-height:16px;"></div>
                </div>
            </div>
            <div id="registerError" class="mt-1" style="font-size:0.82rem;font-weight:600;color:#dc2626;min-height:18px;"></div>
        </form>
    `;
}

function buildUnifiedLoginBodyMarkup() {
    return `
        <ul class="nav auth-premium-tabs" id="loginTabs" role="tablist">
            <li class="nav-item">
                <a class="nav-link active" id="user-login-tab" data-toggle="tab" href="#user-login" role="tab">用户登录</a>
            </li>
            <li class="nav-item">
                <a class="nav-link" id="admin-login-tab" data-toggle="tab" href="#admin-login" role="tab">管理员登录</a>
            </li>
        </ul>
        <div class="tab-content" id="loginTabsContent">
            <div class="tab-pane fade show active" id="user-login" role="tabpanel">
                <form id="userLoginForm">
                    <div class="form-group">
                        <label class="auth-field-label" for="userLoginUsername">用户名 / 邮箱</label>
                        <div class="auth-input-container">
                            <i class="fas fa-user auth-input-icon"></i>
                            <input type="text" class="form-control auth-input-premium" id="userLoginUsername" placeholder="请输入你的账号" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="auth-field-label" for="userLoginPassword">登录密码</label>
                        <div class="auth-input-container">
                            <i class="fas fa-lock auth-input-icon"></i>
                            <div class="auth-password-wrap">
                                <input type="password" class="form-control auth-input-premium" id="userLoginPassword" placeholder="请输入密码" required>
                                <i class="fas fa-eye-slash toggle-password" id="toggleLoginPassword" onclick="togglePasswordVisibility('userLoginPassword','toggleLoginPassword')"></i>
                            </div>
                        </div>
                    </div>
                    <div id="loginError" class="text-danger mb-2" style="font-size: 0.88rem; font-weight: 500;"></div>
                </form>
            </div>
            <div class="tab-pane fade" id="admin-login" role="tabpanel">
                <form id="adminLoginForm">
                    <div class="form-group">
                        <label class="auth-field-label" for="adminLoginUsername">管理员账号</label>
                        <div class="auth-input-container">
                            <i class="fas fa-user-shield auth-input-icon"></i>
                            <input type="text" class="form-control auth-input-premium" id="adminLoginUsername" placeholder="管理员专属账号" required>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="auth-field-label" for="adminLoginPassword">管理员密码</label>
                        <div class="auth-input-container">
                            <i class="fas fa-key auth-input-icon"></i>
                            <div class="auth-password-wrap">
                                <input type="password" class="form-control auth-input-premium" id="adminLoginPassword" placeholder="请输入管理员密码" required>
                                <i class="fas fa-eye-slash toggle-password" id="toggleAdminPassword" onclick="togglePasswordVisibility('adminLoginPassword','toggleAdminPassword')"></i>
                            </div>
                        </div>
                    </div>
                    <div id="adminLoginError" class="text-danger mb-2" style="font-size: 0.88rem; font-weight: 500;"></div>
                </form>
            </div>
        </div>
    `;
}

function buildUnifiedLoginFooterMarkup() {
    return `
        <div class="w-100">
            <button type="button" class="btn btn-primary btn-block auth-btn-gradient" onclick="login()">立即登录</button>
            <div class="auth-footer-links">
                <span>还没有账号？</span>
                <a href="javascript:void(0)" class="auth-link-premium" onclick="showRegisterModal()">立即注册</a>
            </div>
        </div>
    `;
}

function buildUnifiedRegisterFooterMarkup() {
    return `
        <div class="w-100">
            <button type="button" class="btn btn-primary btn-block auth-btn-gradient" id="registerSubmitBtn" onclick="register()">
                <span id="registerBtnText">创建我的账号</span>
                <span id="registerBtnSpinner" style="display:none;">
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    正在努力创建中...
                </span>
            </button>
            <div class="auth-footer-links">
                <span>已有账号？</span>
                <a href="javascript:void(0)" class="auth-link-premium" onclick="showLoginModal()">返回登录</a>
            </div>
        </div>
    `;
}

function installUnifiedAuthOpeners() {
    window.__authUnifiedShowLoginModal = function() {
        try {
            normalizeLoginModalStructure();
        } catch (_) {}
        closeBootstrapModal('#registerModal');
        if (!openBootstrapModal('#loginModal')) {
            redirectToIndexWithAuth('login');
        }
    };

    window.__authUnifiedShowRegisterModal = function() {
        try {
            normalizeRegisterModalStructure();
            normalizeRegisterAgreement();
            bindPolicyLinks();
        } catch (_) {}
        closeBootstrapModal('#loginModal');
        if (!openBootstrapModal('#registerModal')) {
            redirectToIndexWithAuth('register');
        }
    };

    window.showLoginModal = function() {
        try {
            if (typeof window.__authUnifiedShowLoginModal === 'function') {
                return window.__authUnifiedShowLoginModal();
            }
        } catch (_) {}
    };

    window.showRegisterModal = function() {
        try {
            if (typeof window.__authUnifiedShowRegisterModal === 'function') {
                return window.__authUnifiedShowRegisterModal();
            }
        } catch (_) {}
    };
}

function startAuthOpenersTakeoverLoop() {
    if (window.__authOpenersTakeoverStarted) return;
    window.__authOpenersTakeoverStarted = true;

    const startedAt = Date.now();
    const intervalId = setInterval(function() {
        try {
            installUnifiedAuthOpeners();
        } catch (_) {}
        if (Date.now() - startedAt > 3500) {
            try { clearInterval(intervalId); } catch (_) {}
        }
    }, 120);
}

function normalizeRegisterModalStructure() {
    const modal = document.getElementById('registerModal');
    if (!modal) return;

    const modalBody = modal.querySelector('.modal-body');
    const modalFooter = modal.querySelector('.modal-footer');
    const title = modal.querySelector('.modal-title');
    if (!modalBody || !modalFooter) return;

    // NOTE: 检测新版 Premium 结构标记（auth-input-container + auth-input-premium）
    const hasModernStructure = !!(
        modal.querySelector('#registerUsername') &&
        modal.querySelector('#registerEmail') &&
        modal.querySelector('#registerPassword') &&
        modal.querySelector('.auth-input-container') &&
        modal.querySelector('.auth-input-premium')
    );
    const footerLooksUnified = !!modalFooter.querySelector('.auth-btn-gradient');

    if (title) {
        title.textContent = '创建账号';
    }

    // NOTE: 弹窗已显示时绝不替换 innerHTML，避免 Bootstrap backdrop 卡死
    const isCurrentlyShown = modal.classList.contains('show');
    if (!hasModernStructure || !footerLooksUnified) {
        if (!isCurrentlyShown) {
            modalBody.innerHTML = buildUnifiedRegisterFormMarkup();
            modalFooter.innerHTML = buildUnifiedRegisterFooterMarkup();
        }
    }
}

function cleanupStuckBackdrop() {
    try {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(function(bd) { bd.remove(); });
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
        document.body.style.removeProperty('overflow');
    } catch(_) {}
}

function normalizeLoginModalStructure() {
    const modal = document.getElementById('loginModal');
    if (!modal) return;
    // NOTE: 弹窗已显示时绝不替换 innerHTML
    if (modal.classList.contains('show')) return;

    const modalBody = modal.querySelector('.modal-body');
    const modalFooter = modal.querySelector('.modal-footer');
    const title = modal.querySelector('.modal-title');
    if (!modalBody || !modalFooter) return;

    // NOTE: 检测新版 Premium 结构标记（auth-premium-tabs + auth-input-container）
    const hasUnifiedLogin = !!(
        modal.querySelector('#userLoginUsername') &&
        modal.querySelector('#userLoginPassword') &&
        modal.querySelector('.auth-input-container') &&
        modal.querySelector('.auth-premium-tabs')
    );
    const footerLooksUnified = !!modalFooter.querySelector('.auth-btn-gradient');

    if (title) {
        title.textContent = '账号登录';
    }

    if (!hasUnifiedLogin || !footerLooksUnified) {
        modalBody.innerHTML = buildUnifiedLoginBodyMarkup();
        modalFooter.innerHTML = buildUnifiedLoginFooterMarkup();
    }
}

function normalizeRegisterAgreement() {
    const form = document.getElementById('registerForm');
    const modalBody = document.querySelector('#registerModal .modal-body');
    const container = form || modalBody;
    if (!container || container.querySelector('.agreement-notice')) return;

    const oldAgree = container.querySelector('.agree-terms') || document.querySelector('#registerModal .agree-terms');
    const registerError = document.getElementById('registerError');
    const notice = buildAgreementNotice();

    if (oldAgree) {
        const next = oldAgree.nextElementSibling;
        oldAgree.remove();
        if (next && next.tagName === 'DIV' && next.getAttribute('style') && next.textContent.includes('本平台致力于基层癌症早筛')) {
            next.remove();
        }
    }

    document.querySelectorAll('#registerModal [onclick*="服务条款页面建设中"], #registerModal [onclick*="隐私政策页面建设中"], #registerModal [onclick*="医疗信息使用说明"], #registerModal [onclick*="平台用户服务协议"]')
        .forEach(link => {
            const agree = link.closest('.agree-terms');
            if (agree) agree.remove();
        });

    Array.from((container || document).querySelectorAll('div')).forEach(div => {
        const text = (div.textContent || '').replace(/\s+/g, ' ').trim();
        if (text.includes('本平台致力于基层癌症早筛与健康风险评估') && !div.classList.contains('agreement-footnote')) {
            div.remove();
        }
    });

    if (registerError && registerError.parentNode) {
        registerError.parentNode.insertBefore(notice, registerError);
    } else {
        container.appendChild(notice);
    }
}

function bindPolicyLinks() {
    document.querySelectorAll('.agreement-link').forEach(link => {
        if (link.dataset.bound === 'true') return;
        link.dataset.bound = 'true';
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const map = {
                service: '#serviceAgreementModal',
                privacy: '#privacyPolicyModal',
                medical: '#medicalInfoModal'
            };
            const modalId = map[this.dataset.policy];
            if (modalId) openBootstrapModal(modalId);
        });
    });
}

function normalizeAuthUI() {
    injectSharedAuthStyles();
    ensurePolicyModals();
    normalizeLoginModalStructure();
    normalizeRegisterModalStructure();
    removeRegisterPlanSections();
    normalizeRegisterAgreement();
    bindPolicyLinks();
}

// 分时多次执行，兜底把晚插入或被样式覆盖的旧版结构统一掉
function scheduleAuthNormalization() {
    let runs = 0;
    const tick = () => {
        try {
            normalizeLoginModalStructure();
            normalizeRegisterModalStructure();
            normalizeRegisterAgreement();
            bindPolicyLinks();
        } catch (_) {}
        if (++runs < 6) setTimeout(tick, 250);
    };
    setTimeout(tick, 0);
}

function hidePageLoader() {
    const loader = document.getElementById('pageLoader');
    if (!loader) return;
    loader.classList.add('hidden');
    window.setTimeout(() => {
        if (loader && loader.parentNode) {
            loader.style.display = 'none';
        }
    }, 600);
}

function updateGlobalNavbar() {
    try {
        const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
        const username = localStorage.getItem('username') || '用户中心';

        // 找所有"登录/注册"按钮（通过 id 或 onclick 特征）
        const loginBtns = document.querySelectorAll(
            '#navbarLoginBtn, [onclick*="showLoginModal"], [data-target="#loginModal"], [href*="auth=login"]'
        );
        const userBtns = document.querySelectorAll(
            '#navbarUserCenterBtn, [onclick*="user_center"], [href*="user_center.html"]'
        );

        if (isLoggedIn) {
            loginBtns.forEach(btn => {
                // 仅处理导航栏里的登录按钮，不影响页面内容区的按钮
                if (btn.closest('nav, .navbar, header, .navbar-right')) {
                    btn.style.display = 'none';
                }
            });
            userBtns.forEach(btn => {
                if (btn.closest('nav, .navbar, header, .navbar-right')) {
                    btn.style.display = 'inline-block';
                }
            });

            // 如果页面有 navbarLoginBtn 但没有用户下拉，动态创建
            const loginNavBtn = document.getElementById('navbarLoginBtn');
            if (loginNavBtn && !document.getElementById('__authNavUserDropdown')) {
                const drop = document.createElement('div');
                drop.id = '__authNavUserDropdown';
                drop.className = 'dropdown';
                drop.style.cssText = 'display:inline-block;margin-left:10px;';
                const initial = username.charAt(0).toUpperCase();
                drop.innerHTML = `
                    <button class="btn dropdown-toggle d-flex align-items-center" style="background:none;border:1.5px solid #e2e8f0;border-radius:24px;padding:5px 14px 5px 6px;gap:8px;" data-toggle="dropdown">
                        <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#667eea,#764ba2);color:white;font-weight:700;font-size:1rem;display:flex;align-items:center;justify-content:center;">${initial}</div>
                        <span style="font-weight:600;font-size:0.9rem;color:#1a1a2e;max-width:80px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${username}</span>
                        <i class="fas fa-chevron-down" style="font-size:0.7rem;color:#94a3b8;"></i>
                    </button>
                    <div class="dropdown-menu dropdown-menu-right" style="border-radius:14px;border:1px solid #e2e8f0;box-shadow:0 8px 30px rgba(0,0,0,0.1);padding:8px;min-width:180px;">
                        <a class="dropdown-item" href="user_center.html" style="border-radius:8px;padding:10px 14px;font-weight:500;"><i class="fas fa-user-circle mr-2 text-primary"></i>个人中心</a>
                        <div class="dropdown-divider" style="margin:6px 0;"></div>
                        <a class="dropdown-item text-danger" href="#" onclick="localStorage.removeItem('isLoggedIn');localStorage.removeItem('username');window.location.href='index.html';" style="border-radius:8px;padding:10px 14px;font-weight:500;"><i class="fas fa-sign-out-alt mr-2"></i>退出登录</a>
                    </div>`;
                loginNavBtn.parentNode.insertBefore(drop, loginNavBtn.nextSibling);
                loginNavBtn.style.display = 'none';
            }
        } else {
            loginBtns.forEach(btn => {
                if (btn.closest('nav, .navbar, header, .navbar-right')) {
                    btn.style.display = '';
                }
            });
            userBtns.forEach(btn => {
                if (btn.closest('nav, .navbar, header, .navbar-right')) {
                    btn.style.display = 'none';
                }
            });
        }
    } catch(_) {}
}

// 登录成功后调用此函数更新状态
window.onLoginSuccess = function(userData) {
    try {
        localStorage.setItem('isLoggedIn', 'true');
        if (userData && userData.username) localStorage.setItem('username', userData.username);
        if (userData && userData.email) localStorage.setItem('email', userData.email);
        updateGlobalNavbar();
    } catch(_) {}
};

function __runAuthBootstrap() {
    installUnifiedAuthOpeners();
    startAuthOpenersTakeoverLoop();
    normalizeAuthUI();
    updateGlobalNavbar();
    hidePageLoader();
    attachModalNormalization();
    attachDelegatedOpeners();
    observeAddedModals();
    scheduleAuthNormalization();
    // 对页面里已有的 modal，立即开始监听可见性
    try {
        const reg = document.getElementById('registerModal');
        const log = document.getElementById('loginModal');
        if (reg) watchModalVisibility(reg);
        if (log) watchModalVisibility(log);
    } catch (_) {}
    try {
        const params = new URLSearchParams(window.location.search);
        const auth = (params.get('auth') || '').toLowerCase();
        if (auth === 'login') {
            setTimeout(() => window.showLoginModal && window.showLoginModal(), 0);
        }
        if (auth === 'register') {
            setTimeout(() => window.showRegisterModal && window.showRegisterModal(), 0);
        }
    } catch (_) {
        // ignore
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', __runAuthBootstrap);
} else {
    // DOM 已经解析完成（interactive/complete），立刻运行
    setTimeout(__runAuthBootstrap, 0);
}

window.addEventListener('load', hidePageLoader);

// 在所有脚本（可能定义了旧版 show*）加载完成后，再次覆盖为统一版本
window.addEventListener('load', function() {
    installUnifiedAuthOpeners();
    startAuthOpenersTakeoverLoop();
    normalizeLoginModalStructure();
    normalizeRegisterModalStructure();
    normalizeRegisterAgreement();
    bindPolicyLinks();
    [0, 120, 300, 700, 1200].forEach(function(delay) {
        setTimeout(function() {
            try {
                installUnifiedAuthOpeners();
                startAuthOpenersTakeoverLoop();
                normalizeLoginModalStructure();
                normalizeRegisterModalStructure();
                normalizeRegisterAgreement();
                bindPolicyLinks();
            } catch (_) {}
        }, delay);
    });
});

// 暴露全局清理函数，并监听 modal 关闭事件自动清理残留 backdrop
window.cleanupStuckBackdrop = cleanupStuckBackdrop;

// Bootstrap 4 modal 事件必须用 jQuery 监听
function bindBackdropCleanup() {
    if (!window.jQuery) {
        setTimeout(bindBackdropCleanup, 200);
        return;
    }
    const $ = window.jQuery;

    // 弹窗显示前：替换结构（此时 show 类还未加，normalizeXxx 内的 isCurrentlyShown 为 false）
    $(document).on('show.bs.modal', '#registerModal', function() {
        try {
            injectSharedAuthStyles();
            normalizeRegisterModalStructure();
            normalizeRegisterAgreement();
            bindPolicyLinks();
        } catch(_) {}
    });
    $(document).on('show.bs.modal', '#loginModal', function() {
        try {
            injectSharedAuthStyles();
            normalizeLoginModalStructure();
        } catch(_) {}
    });

    // 弹窗显示后：应用内联样式（dialog 宽度等）
    $(document).on('shown.bs.modal', '#registerModal, #loginModal', function() {
        try { applyModalInlineStyles(this.id); } catch(_) {}
    });

    // 弹窗关闭后：清理 backdrop
    $(document).on('hidden.bs.modal', function() {
        setTimeout(cleanupStuckBackdrop, 50);
    });
    $(document).on('hide.bs.modal', function() {
        setTimeout(cleanupStuckBackdrop, 450);
    });
}
bindBackdropCleanup();

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
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    if (score <= 2) return 'weak';
    if (score <= 3) return 'medium';
    return 'strong';
}

const STRENGTH_LABELS = {
    weak: '弱 — 至少8位，需含字母和数字',
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
 * 校验用户名格式：3-20 位，支持中文、字母、数字、下划线
 * @param username 用户名
 * @returns boolean
 */
function isValidUsername(username) {
    // 支持中文、字母、数字、下划线，长度3-20
    return /^[\u4e00-\u9fa5a-zA-Z0-9_]{3,20}$/.test(username);
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
                if (hint) { hint.textContent = '用户名3-20位，支持中文、字母、数字或下划线'; hint.className = 'input-hint error'; }
            }
        });
    }

    // 兼容两种邮箱输入模式：1) 传统完整邮箱 2) 前缀+域名下拉
    const emailPrefixInput = document.getElementById('registerEmailPrefix');
    if (emailPrefixInput) {
        // 邮箱前缀+域名下拉模式：实时同步到隐藏的 registerEmail
        const syncEmail = function() {
            const prefix = emailPrefixInput.value.trim();
            const domainSel = document.getElementById('registerEmailDomain');
            const domain = domainSel ? domainSel.value : 'qq.com';
            const hint = document.getElementById('emailHint');
            if (emailInput) emailInput.value = prefix ? (prefix + '@' + domain) : '';
            if (!prefix) {
                emailPrefixInput.classList.remove('is-valid', 'is-invalid');
                if (hint) { hint.textContent = ''; hint.className = 'input-hint'; }
                return;
            }
            // 只校验前缀合法性（不含@和空格）
            if (/^[a-zA-Z0-9._-]+$/.test(prefix)) {
                emailPrefixInput.classList.remove('is-invalid');
                emailPrefixInput.classList.add('is-valid');
                if (hint) { hint.textContent = '✓ ' + prefix + '@' + domain; hint.className = 'input-hint success'; }
            } else {
                emailPrefixInput.classList.remove('is-valid');
                emailPrefixInput.classList.add('is-invalid');
                if (hint) { hint.textContent = '邮箱前缀仅限字母、数字、点、下划线、横线'; hint.className = 'input-hint error'; }
            }
        };
        emailPrefixInput.addEventListener('input', syncEmail);
        const domainSel = document.getElementById('registerEmailDomain');
        if (domainSel) domainSel.addEventListener('change', syncEmail);
    } else if (emailInput) {
        // 传统完整邮箱输入模式（admin_dashboard等页面）
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
    const phone = document.getElementById('registerPhone')?.value?.trim() || '';
    const password = document.getElementById('registerPassword')?.value;
    const confirmPassword = document.getElementById('confirmPassword')?.value;
    const errorDiv = document.getElementById('registerError');

    // 优先从 prefix+domain 组装邮箱，否则取完整邮箱输入框
    let email = '';
    const emailPrefixEl = document.getElementById('registerEmailPrefix');
    const emailDomainEl = document.getElementById('registerEmailDomain');
    if (emailPrefixEl && emailDomainEl && emailPrefixEl.value.trim()) {
        email = emailPrefixEl.value.trim() + '@' + emailDomainEl.value;
    } else {
        email = document.getElementById('registerEmail')?.value?.trim() || '';
    }

    if (errorDiv) errorDiv.textContent = '';

    // ---- 前端校验 ----
    if (!username || !email || !password) {
        if (errorDiv) errorDiv.textContent = '请填写所有必填项（用户名、邮箱、密码）';
        return;
    }

    if (!isValidUsername(username)) {
        if (errorDiv) errorDiv.textContent = '用户名3-20位，支持中文、字母、数字或下划线';
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

    if (password.length < 8) {
        if (errorDiv) errorDiv.textContent = '密码长度至少8位，需包含字母和数字';
        return;
    }

    if (!/[a-zA-Z]/.test(password) || !/\d/.test(password)) {
        if (errorDiv) errorDiv.textContent = '密码需同时包含字母和数字';
        return;
    }

    if (password !== confirmPassword) {
        if (errorDiv) errorDiv.textContent = '两次输入的密码不一致';
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
            localStorage.setItem('plan', data.user.plan || 'free');
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
    localStorage.removeItem('plan');
    localStorage.removeItem('token');
    localStorage.removeItem('X-Admin-Token');
    localStorage.removeItem('predictionResult');
    showToast('info', '已安全退出登录');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 800);
};
// ============================================================
// 注册合规提示工具 (Premium 紧凑版)
// ============================================================

function buildAgreementNotice() {
    const notice = document.createElement('div');
    notice.id = 'medicalNotice';
    notice.style.cssText = `
        background: rgba(37, 99, 235, 0.04);
        border: 1px solid rgba(37, 99, 235, 0.1);
        border-radius: 12px;
        padding: 8px 12px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    `;
    
    notice.innerHTML = `
        <div style="color: #2563eb; font-size: 14px;"><i class="fas fa-shield-alt"></i></div>
        <div style="flex: 1;">
            <p style="margin: 0; font-size: 0.72rem; line-height: 1.3; color: #64748b;">
                同意 <a href="#" style="color:#2563eb;font-weight:600;text-decoration:none;">《服务协议》</a>。平台结果仅供健康管理参考，不作为诊断依据。
            </p>
        </div>
    `;
    return notice;
}

function normalizeRegisterAgreement() {
    const registerModal = document.getElementById('registerModal');
    if (!registerModal) return;
    
    const container = registerModal.querySelector('.modal-body') || registerModal.querySelector('form');
    if (!container) return;

    if (document.getElementById('medicalNotice')) return;

    const notice = buildAgreementNotice();
    const registerError = document.getElementById('registerError');
    if (registerError) {
        registerError.parentNode.insertBefore(notice, registerError);
    } else {
        container.appendChild(notice);
    }
}

function bindPolicyLinks() {
    // 绑定协议点击事件
    document.querySelectorAll('.auth-link-premium').forEach(link => {
        if(link.textContent.includes('协议') || link.textContent.includes('政策')) {
            link.onclick = (e) => {
                e.preventDefault();
                showToast('info', '正在加载相关隐私政策与用户协议...');
            };
        }
    });
}
