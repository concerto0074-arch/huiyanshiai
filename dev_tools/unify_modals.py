"""
批量将所有前端 HTML 页面中的 loginModal 和 registerModal 替换为统一干净骨架。
auth.js 会在页面加载后自动注入统一的 Premium 样式和表单内容。
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


def extract_modal_block(content, modal_id):
    """提取完整的 modal div 块（通过计数 div 层级来找结束位置）"""
    pattern = re.compile(
        r'(?:<!--[^\-].*?-->\s*)?' +
        r'<div[^>]+id=["\']' + re.escape(modal_id) + r'["\'][^>]*>',
        re.DOTALL
    )
    m = pattern.search(content)
    if not m:
        return None, None, None

    start = m.start()
    # 找到 <div id="..."> 的位置，从这里开始计数层级
    tag_start = content.index('<div', m.start())
    depth = 0
    i = tag_start

    # 使用正则逐个扫描 <div> 和 </div>
    token_re = re.compile(r'(<div[\s>])|(<\/div>)', re.IGNORECASE)
    for tm in token_re.finditer(content, tag_start):
        if tm.group(1):  # opening <div
            depth += 1
        elif tm.group(2):  # closing </div>
            depth -= 1
            if depth == 0:
                end = tm.end()
                return start, end, content[start:end]
    return None, None, None


def replace_modal(content, modal_id, skeleton):
    """替换 content 中第一个匹配的 modal，移除所有重复的同 ID modal"""
    replaced = False
    result = content

    # 循环移除所有同 ID 的 modal，只保留替换后的一个
    iterations = 0
    while iterations < 10:
        iterations += 1
        start, end, block = extract_modal_block(result, modal_id)
        if start is None:
            break
        if not replaced:
            result = result[:start] + skeleton + result[end:]
            replaced = True
        else:
            # 移除重复的
            result = result[:start] + result[end:]

    return result, replaced


changed = 0
skipped = 0

for fpath in sorted(glob.glob(FRONTEND + '/*.html')):
    fname = os.path.basename(fpath)

    # 跳过 admin_dashboard（有独立的登录逻辑，不动）
    # if fname == 'admin_dashboard.html':
    #     skipped += 1
    #     continue

    with open(fpath, 'r', encoding='utf-8') as f:
        original = f.read()

    content = original

    # 替换 loginModal
    content, login_changed = replace_modal(content, 'loginModal', LOGIN_SKELETON)
    # 替换 registerModal
    content, reg_changed = replace_modal(content, 'registerModal', REGISTER_SKELETON)

    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[OK] {fname}')
        changed += 1
    else:
        print(f'[--] {fname} (no change)')
        skipped += 1

print(f'\n完成: {changed} 个文件已更新, {skipped} 个无变化')
