"""
修复 group.html / products.html / user_center.html 三个文件：
在 loginModal 起始行之前截断，追加干净的骨架 modal。
"""
import os

FRONTEND = r'd:\huiyanshiai(2.0)\frontend'

SKELETON = """
<!-- 登录模态框 -->
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
</div>

<!-- 注册模态框 -->
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
</div>

<div id="toastContainer"></div>
<script src="js/auth.js"></script>
</body>
</html>
"""

FILES = {
    'group.html': 'loginModal',
    'products.html': 'loginModal',
    'user_center.html': 'loginModal',
}

for fname, marker_id in FILES.items():
    fpath = os.path.join(FRONTEND, fname)
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    # 找到第一个包含 loginModal 的行
    cut_idx = None
    for i, line in enumerate(lines):
        if f'id="{marker_id}"' in line:
            cut_idx = i
            break

    if cut_idx is None:
        print(f'[SKIP] {fname}: marker not found')
        continue

    # 保留 cut_idx 之前的所有行（去掉末尾空行）
    kept = lines[:cut_idx]
    # 去掉末尾多余空行
    while kept and kept[-1].strip() == '':
        kept.pop()

    new_content = ''.join(kept) + SKELETON

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'[OK] {fname}: cut at line {cut_idx + 1}, kept {len(kept)} lines')
