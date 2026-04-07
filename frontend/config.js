/**
 * 慧眼识癌 (HuiYanShiAi) - 全局前端配置文件
 * 使用这段代码可自动在本地环境与线上生产环境之间切换后端接口地址。
 * Deploy Trigger: 2026-03-26
 */

(function() {
    // 获取当前网页的域名
    const hostname = window.location.hostname;
    const protocol = window.location.protocol;
    const origin = window.location.origin;
    const port = window.location.port;
    
    // 判断是否在本地运行 (本地开发可能是 localhost 或 127.0.0.1)
    const isLocal = (hostname === 'localhost' || hostname === '127.0.0.1');
    
    // ⚠️ 重要：请将下面的地址替换为您在 Render 上实际部署的后端 URL
    // 格式通常为: https://huiyanshiai-api.onrender.com （不要带末尾斜杠）
    // 您可以在 Render Dashboard → 您的 Web Service → Settings 中找到该地址
    const PRODUCTION_API_URL = "https://huiyanshiai-api.onrender.com";
    
    // 运行时确定最终的后端地址
    // 如果由后端本地服务提供页面，则直接使用同源；否则回退到本地后端固定端口 5000
    const backendUrl = isLocal
        ? (port === '5000' ? origin : 'http://127.0.0.1:5000')
        : PRODUCTION_API_URL;
    
    // 挂载到全局 window 对象上，供各个页面的 JS 使用
    window.APP_CONFIG = {
        API_BASE_URL: backendUrl,
        IS_LOCAL: isLocal
    };

    // Hide injected toolbars/overlays (e.g. preview toolbars) to keep UI consistent
    try {
        const style = document.createElement('style');
        style.setAttribute('data-hysai-global-overrides', 'true');
        style.textContent = `
            #__vercel,
            #vercel-toolbar,
            [data-vercel-toolbar],
            iframe[title*="Vercel" i],
            iframe[src*="vercel.com" i][src*="toolbar" i],
            iframe[src*="vercel.app" i][src*="toolbar" i] {
                display: none !important;
                visibility: hidden !important;
                opacity: 0 !important;
                pointer-events: none !important;
            }
        `;
        document.head.appendChild(style);
    } catch (e) {
        // ignore
    }

    try {
        const hideBottomLeftOverlays = () => {
            const vw = window.innerWidth || document.documentElement.clientWidth || 0;
            const vh = window.innerHeight || document.documentElement.clientHeight || 0;
            if (!vw || !vh) return;

            const candidates = Array.from(document.body.querySelectorAll('*'));
            for (const el of candidates) {
                if (!(el instanceof HTMLElement)) continue;
                if (el.closest('[data-hysai-global-overrides]')) continue;
                const cs = window.getComputedStyle(el);
                if (cs.position !== 'fixed') continue;
                if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') continue;

                const rect = el.getBoundingClientRect();
                if (rect.width <= 0 || rect.height <= 0) continue;

                const nearLeft = rect.left <= 20;
                const nearBottom = rect.bottom >= (vh - 20);
                const small = rect.width <= 220 && rect.height <= 90;

                if (!nearLeft || !nearBottom || !small) continue;

                const interactiveCount = el.querySelectorAll('button, a, svg, img, i').length;
                if (interactiveCount === 0 || interactiveCount > 12) continue;

                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('visibility', 'hidden', 'important');
                el.style.setProperty('opacity', '0', 'important');
                el.style.setProperty('pointer-events', 'none', 'important');
            }
        };

        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            window.setTimeout(hideBottomLeftOverlays, 50);
            window.setTimeout(hideBottomLeftOverlays, 600);
            window.setTimeout(hideBottomLeftOverlays, 1500);
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                window.setTimeout(hideBottomLeftOverlays, 50);
                window.setTimeout(hideBottomLeftOverlays, 600);
                window.setTimeout(hideBottomLeftOverlays, 1500);
            });
        }
    } catch (e) {
        // ignore
    }
    
    console.log(`[开发提示] 当前环境: ${isLocal ? '本地开发' : '线上生产'}`);
    console.log(`[开发提示] 后端API已自动指向: ${backendUrl}`);
})();
