"""
修补脚本：处理使用 navbar-nav ml-auto 的页面
"""
import os

NAV_ITEMS = [
    ('index.html', '首页', 'index'),
    ('algorithms.html', 'AI风险预测', 'algorithms'),
    ('products.html', '产品服务', 'products'),
    ('group.html', '团体方案', 'group'),
    ('experts.html', '专家在线', 'experts'),
    ('knowledge.html', '知识科普', 'knowledge'),
    ('cases.html', '客户案例', 'cases'),
]

def build_nav_ul(active_page, css_class):
    lines = []
    for href, label, key in NAV_ITEMS:
        cls = 'nav-link active' if active_page == key else 'nav-link'
        lines.append(f'                    <li class="nav-item"><a class="{cls}" href="{href}">{label}</a></li>')
    return '\n'.join(lines)

def process(filepath, active_page):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # 尝试匹配两种class
    for css_class in ['navbar-nav mx-auto', 'navbar-nav ml-auto']:
        ul_start = f'<ul class="{css_class}">'
        ul_end = '</ul>'
        idx_s = content.find(ul_start)
        if idx_s != -1:
            idx_e = content.find(ul_end, idx_s)
            if idx_e != -1:
                new_ul = f'{ul_start}\n{build_nav_ul(active_page, css_class)}\n                {ul_end}'
                content = content[:idx_s] + new_ul + content[idx_e + len(ul_end):]
                break

    # 移除悬停CSS
    hover_start = '    <!-- 悬停展开下拉菜单优化 -->'
    if hover_start in content:
        h_idx = content.find(hover_start)
        style_end = '</style>'
        h_end = content.find(style_end, h_idx)
        if h_end != -1:
            block_end = h_end + len(style_end)
            while block_end < len(content) and content[block_end] in '\r\n':
                block_end += 1
            content = content[:h_idx] + content[block_end:]

    # 统一副标题
    for old_sub in ['癌症风险综合预测平台', '您身边的癌症预防专家', 'AI·癌症风险综合预测平台']:
        content = content.replace(old_sub, '基层早筛的AI普惠型平台')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'[OK] {os.path.basename(filepath)}')
    else:
        print(f'[NO CHANGE] {os.path.basename(filepath)}')

if __name__ == '__main__':
    html_dir = r'd:\huiyanshiai(2.0)\frontend'
    targets = ['report.html', 'article-detail-9.html', 'article-detail-10.html']
    for fn in targets:
        fp = os.path.join(html_dir, fn)
        if os.path.exists(fp):
            process(fp, 'knowledge' if fn.startswith('article') else 'none')
