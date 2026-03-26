/**
 * 慧眼识癌 (HuiYanShiAi) - 全局前端配置文件
 * 使用这段代码可自动在本地环境与线上生产环境之间切换后端接口地址。
 */

(function() {
    // 获取当前网页的域名
    const hostname = window.location.hostname;
    
    // 判断是否在本地运行 (本地开发可能是 localhost 或 127.0.0.1)
    const isLocal = (hostname === 'localhost' || hostname === '127.0.0.1');
    
    // 您未来真实的公网后端地址放在下面：
    // （如果您的云服务提供商给了您其他地址，例如 Render，您可以直接修改这一行）
    const PRODUCTION_API_URL = "https://api.huiyanshiai.com";
    
    // 运行时确定最终的后端地址
    const backendUrl = isLocal ? "http://localhost:5001" : PRODUCTION_API_URL;
    
    // 挂载到全局 window 对象上，供各个页面的 JS 使用
    window.APP_CONFIG = {
        API_BASE_URL: backendUrl,
        IS_LOCAL: isLocal
    };
    
    console.log(`[开发提示] 当前环境: ${isLocal ? '本地开发' : '线上生产'}`);
    console.log(`[开发提示] 后端API已自动指向: ${backendUrl}`);
})();
