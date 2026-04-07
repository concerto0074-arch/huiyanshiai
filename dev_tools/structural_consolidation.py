from pathlib import Path
import re
import os

path = Path(r"d:\huiyanshiai(2.0)\frontend\algorithms.html")
text = path.read_text(encoding="utf-8")

# 1. 移除冗余嵌套的 .container 容器
# 移除工作台周围的 container
text = re.sub(
    r'<!-- 交互式预测工作台 -->\s*<div class="container">',
    r'<!-- 交互式预测工作台 -->',
    text
)
# 移除深度解析板块周围的 container
text = re.sub(
    r'<!-- =============== 核心算法深度解析板块 =============== -->\s*<div class="container">',
    r'<!-- =============== 核心算法深度解析板块 =============== -->',
    text
)

# 注意：由于去掉了内部 container，需要确保外面只有一个大的 container 或者这些板块都是独立的顶级 container。
# 目前结构是：<div class="container"> (Main) -> ... -> </div> (End at 2082)
# 检查是否有多余的闭合 </div>
# 在工作台结束处可能有余出的 </div>
text = text.replace('</div>\n            </div>\n        </div>\n    </div>\n\n    <!-- =============== 核心算法深度解析板块', '</div>\n            </div>\n        </div>\n\n    <!-- =============== 核心算法深度解析板块')

# 2. 统一预测工作台的卡片样式
# 左侧输入区
text = re.sub(
    r'<div class="col-lg-5 mb-4 mb-lg-0">\s*<div class="algorithm-card" style="padding: 20px;">',
    r'<div class="col-lg-5 mb-4 mb-lg-0">\n                    <div class="algorithm-card" style="height: 100%; margin-bottom: 0 !important;">',
    text
)
# 右侧选择区
text = re.sub(
    r'<div class="col-lg-7">\s*<div style="background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.06); padding: 15px 20px; border: 1px solid #eef2f7; display: flex; flex-direction: column;">',
    r'<div class="col-lg-7">\n                    <div class="algorithm-card" style="height: 100%; display: flex; flex-direction: column; margin-bottom: 0 !important;">',
    text
)

# 3. 优化卡片内的 Padding
# 将内联的 padding: 20px 统一处理或保留，但移除多余的 background/border 定义
text = text.replace('background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.06); padding: 15px 20px; border: 1px solid #eef2f7;', 'padding: 20px;')

# 4. 彻底解决 modal grayed-out 问题 - 确保 CSS 定义最强且唯一
# 移除 head 中零散的样式定义，确保只保留 final_css 块中的定义
text = re.sub(
    r'\/\* 模态框层级与遮罩修复 \*\/.*?body\.modal-open \{.*?\}',
    r'''/* 模态框层级与遮罩修复 */
        .modal-backdrop {
            z-index: 1040 !important;
            background-color: rgba(0, 0, 0, 0.5) !important;
            opacity: 0.5 !important;
        }
        .modal {
            z-index: 1050 !important;
            pointer-events: auto !important;
        }
        .modal-content {
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 20px 60px rgba(0,0,0,0.15) !important;
            pointer-events: auto !important;
        }
        body.modal-open {
            overflow: hidden !important;
            padding-right: 0 !important;
        }''',
    text,
    flags=re.DOTALL
)

# 5. 清理脚本
for f in os.listdir(r"d:\huiyanshiai(2.0)"):
    if (f.startswith("tmp_") or f.startswith("fix_") or f.startswith("cleanup_") or f.startswith("final_") or f.startswith("perfect_") or f == "ultimate_cleanup.py" or f == "final_polish_v4.py") and f.endswith(".py"):
        try:
            os.remove(os.path.join(r"d:\huiyanshiai(2.0)", f))
        except:
            pass

path.write_text(text, encoding="utf-8")
print("HTML structure consolidated and modal styles reinforced.")
