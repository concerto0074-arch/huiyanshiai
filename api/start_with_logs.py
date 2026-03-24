import sys
import os
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='server_start.log',
    filemode='w'
)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)

logger.info("开始启动服务器...")
logger.info(f"Python版本: {sys.version}")
logger.info(f"当前工作目录: {os.getcwd()}")
logger.info(f"Python路径: {sys.path}")

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
logger.info(f"更新后的Python路径: {sys.path}")

try:
    logger.info("导入Flask...")
    from flask import Flask
    logger.info("Flask导入成功")
    
    logger.info("导入数据库模块...")
    import database
    logger.info("数据库模块导入成功")
    
    logger.info("导入模型模块...")
    from models.simulated_model import predict_probability, get_risk_level
    logger.info("模型模块导入成功")
    
    logger.info("导入app模块...")
    import app
    logger.info("app模块导入成功")
    
    logger.info("启动服务器...")
    app.app.run(host='0.0.0.0', port=5000, debug=True)
except Exception as e:
    logger.error(f"启动失败: {type(e).__name__}: {e}")
    import traceback
    logger.error(traceback.format_exc())
    print(f"启动失败: {type(e).__name__}: {e}")
    traceback.print_exc()
