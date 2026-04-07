"""
对所有前端页面：
- 若 loginModal 和 registerModal 都不存在，在 auth.js script 标签之前插入骨架
- 若只有 registerModal（无 loginModal），也补上 loginModal 骨架
- 若存在旧版 modal（body 非空），用骨架替换
"""
import re
import os
import glob

FRONTEND = r'd:\huiyanshiai(2.0)\frontend'

LOGIN_SKELETON = """<!-- 登录模态框 -->
<div class="modal fade" id="loginModal" tabindex="-1" role="dialog" aria-labelledby="loginModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="loginModalLabel">账号登录</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            </div>
            <div class="modal-body"></div>
            <div class="modal-footer"></div>
        </div>
    </div>
</div>"""

REGISTER_SKELETON = """<!-- 注册模态框 -->
<div class="modal fade" id="registerModal" tabindex="-1" role="dialog" aria-labelledby="registerModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered" role="document">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="registerModalLabel">创建账号</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            </div>
            <div class="modal-body"></div>
            <div class="modal-footer"></div>
        </div>
    </div>
</div>"""

AUTH_JS_PATTERN = re.compile(r'(<script[^>]+src=["\']js/auth\.js["\'][^>]*></script>)', re.IGNORECASE)


def has_modal(content, modal_id):
    return bool(re.search(r'id=["\']' + re.escape(modal_id) + r'["\']', content))


def modal_body_is_empty(content, modal_id):
    """检查 modal-body 是否为空（只有空白）"""
    m = re.search(r'id=["\']' + re.escape(modal_id) + r'"[\s\S]{0,500}modal-body">([\s]*)</div>', content)
    return bool(m)


def extract_and_replace_modal(content, modal_id, skeleton):
    """找到旧版 modal block，用骨架替换"""
    # 找 modal 开始位置
    start_m = re.search(r'(?:<!--[^\n]*-->\s*)?\n?<div[^>]+id=["\']' + re.escape(modal_id) + r'["\'][^>]*>', content)
    if not start_m:
        return content, False

    start = start_m.start()
    tag_start = content.index('<div', start_m.start())

    # 用正则逐个扫描 <div> 和 </div>
    token_re = re.compile(r'(<div[\s>])|(<\/div>)', re.IGNORECASE)
    depth = 0
    end = None
    for tm in token_re.finditer(content, tag_start):
        if tm.group(1):
            depth += 1
        elif tm.group(2):
            depth -= 1
            if depth == 0:
                end = tm.end()
                break

    if end is None:
        return content, False

    return content[:start] + skeleton + '\n' + content[end:].lstrip('\n'), True


changed = 0
skipped = 0

for fpath in sorted(glob.glob(FRONTEND + '/*.html')):
    fname = os.path.basename(fpath)

    # 跳过纯管理/登录页
    if fname in ('admin_login.html', 'test_api.html', 'test_modal.html'):
        continue

    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        original = f.read()

    content = original
    modified = False

    has_login = has_modal(content, 'loginModal')
    has_register = has_modal(content, 'registerModal')

    if not has_login and not has_register:
        # 在 auth.js 前插入两个骨架
        if AUTH_JS_PATTERN.search(content):
            insert = '\n' + LOGIN_SKELETON + '\n\n' + REGISTER_SKELETON + '\n\n'
            content = AUTH_JS_PATTERN.sub(insert + r'\1', content)
            modified = True
        else:
            print(f'[WARN] {fname}: no auth.js reference found, skipping')
            skipped += 1
            continue

    else:
        # 替换旧版（非空 body）或补缺失的
        if has_login:
            content, did = extract_and_replace_modal(content, 'loginModal', LOGIN_SKELETON)
            if did:
                modified = True

        if has_register:
            content, did = extract_and_replace_modal(content, 'registerModal', REGISTER_SKELETON)
            if did:
                modified = True

        if not has_login:
            if AUTH_JS_PATTERN.search(content):
                content = AUTH_JS_PATTERN.sub('\n' + LOGIN_SKELETON + '\n\n' + r'\1', content)
                modified = True

        if not has_register:
            if AUTH_JS_PATTERN.search(content):
                content = AUTH_JS_PATTERN.sub('\n' + REGISTER_SKELETON + '\n\n' + r'\1', content)
                modified = True

    if modified and content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[OK] {fname}')
        changed += 1
    else:
        print(f'[--] {fname}')
        skipped += 1

print(f'\n完成: {changed} 个文件已更新, {skipped} 个跳过')
