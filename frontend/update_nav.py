"""
批量替换导航栏为7项平铺结构（无下拉菜单）：
首页 | AI风险预测 | 产品服务 | 团体方案 | 专家在线 | 知识科普 | 客户案例
"""
import os

# 页面对应的 active 标记
PAGES = {
    'index.html': 'index',
    'algorithms.html': 'algorithms',
    'products.html': 'products',
    'group.html': 'group',
    'experts.html': 'experts',
    'knowledge.html': 'knowledge',
    'cases.html': 'cases',
    'user_center.html': 'none',
    'report.html': 'none',
}

NAV_ITEMS = [
    ('index.html', '首页', 'index'),
    ('algorithms.html', 'AI风险预测', 'algorithms'),
    ('products.html', '产品服务', 'products'),
    ('group.html', '团体方案', 'group'),
    ('experts.html', '专家在线', 'experts'),
    ('knowledge.html', '知识科普', 'knowledge'),
    ('cases.html', '客户案例', 'cases'),
]


def build_nav_ul(active_page):
    lines = []
    for href, label, key in NAV_ITEMS:
        cls = 'nav-link active' if active_page == key else 'nav-link'
        lines.append(f'                    <li class="nav-item"><a class="{cls}" href="{href}">{label}</a></li>')
    return '\n'.join(lines)


def process(filepath, active_page):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. 找到 <ul class="navbar-nav mx-auto"> ... </ul> 并替换内容
    ul_start = '<ul class="navbar-nav mx-auto">'
    ul_end = '</ul>'
    idx_s = content.find(ul_start)
    if idx_s == -1:
        print(f'[SKIP] {os.path.basename(filepath)} - 未找到导航ul')
        return
    idx_e = content.find(ul_end, idx_s)
    if idx_e == -1:
        print(f'[SKIP] {os.path.basename(filepath)} - 未找到导航ul结束')
        return

    new_ul = f'{ul_start}\n{build_nav_ul(active_page)}\n                {ul_end}'
    content = content[:idx_s] + new_ul + content[idx_e + len(ul_end):]

    # 2. 移除悬停CSS块和隐藏箭头CSS（不再需要）
    # 删掉 <!-- 悬停展开下拉菜单优化 --> ... </style> 块
    hover_start = '    <!-- 悬停展开下拉菜单优化 -->'
    if hover_start in content:
        h_idx = content.find(hover_start)
        # 找到这个style块的结束 </style>
        style_end = '</style>'
        h_end = content.find(style_end, h_idx)
        if h_end != -1:
            # 删掉整个块（包含换行）
            block_end = h_end + len(style_end)
            # 跳过后面的换行
            while block_end < len(content) and content[block_end] in '\r\n':
                block_end += 1
            content = content[:h_idx] + content[block_end:]

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[OK] {os.path.basename(filepath)}')
    else:
        print(f'[NO CHANGE] {os.path.basename(filepath)}')


if __name__ == '__main__':
    html_dir = r'd:\huiyanshiai(2.0)\frontend'

    for filename, active in PAGES.items():
        fp = os.path.join(html_dir, filename)
        if os.path.exists(fp):
            process(fp, active)
        else:
            print(f'[MISS] {filename}')

    # article-detail 页面
    for f in sorted(os.listdir(html_dir)):
        if f.startswith('article-detail') and f.endswith('.html'):
            process(os.path.join(html_dir, f), 'knowledge')
