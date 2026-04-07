"""
截断 cases.html 和 experts.html 在 loginModal 之前，追加干净骨架。
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

for fname in ['cases.html', 'experts.html']:
    fpath = os.path.join(FRONTEND, fname)
    with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    cut_idx = None
    for i, line in enumerate(lines):
        if 'id="loginModal"' in line:
            cut_idx = i
            break

    if cut_idx is None:
        print(f'[SKIP] {fname}: loginModal not found')
        continue

    kept = lines[:cut_idx]
    while kept and kept[-1].strip() == '':
        kept.pop()

    new_content = ''.join(kept) + SKELETON

    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f'[OK] {fname}: cut at line {cut_idx + 1}, kept {len(kept)} lines')
