# 工具函数

import pandas as pd
import joblib
import os
import logging
from config import LOG_LEVEL, LOG_FORMAT

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)
    return logging.getLogger(__name__)

logger = setup_logging()

def ensure_dir(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"创建目录: {directory}")
    return directory

def load_data(file_path):
    """加载数据"""
    logger.info(f"加载数据: {file_path}")
    data = pd.read_csv(file_path)
    logger.info(f"数据加载完成，共{len(data)}个样本")
    return data

def save_data(data, file_path):
    """保存数据"""
    ensure_dir(os.path.dirname(file_path))
    data.to_csv(file_path, index=False)
    logger.info(f"数据已保存到: {file_path}")

def save_model(model, model_path):
    """保存模型"""
    ensure_dir(os.path.dirname(model_path))
    joblib.dump(model, model_path)
    logger.info(f"模型已保存到: {model_path}")

def load_model(model_path):
    """加载模型"""
    logger.info(f"加载模型: {model_path}")
    return joblib.load(model_path)

def save_results(results, results_path):
    """保存结果"""
    ensure_dir(os.path.dirname(results_path))
    joblib.dump(results, results_path)
    logger.info(f"结果已保存到: {results_path}")

def load_results(results_path):
    """加载结果"""
    logger.info(f"加载结果: {results_path}")
    return joblib.load(results_path)

def get_feature_importance(model, feature_names):
    """获取特征重要性"""
    try:
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            return feature_importance
        elif hasattr(model.named_steps['model'], 'feature_importances_'):
            importances = model.named_steps['model'].feature_importances_
            feature_importance = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False)
            return feature_importance
        else:
            logger.warning("模型不支持特征重要性计算")
            return None
    except Exception as e:
        logger.error(f"计算特征重要性失败: {str(e)}")
        return None

def get_model_name_from_path(model_path):
    """从模型路径获取模型名称"""
    return os.path.basename(model_path).replace('_model.joblib', '')

def get_model_path(model_name, models_dir='models'):
    """获取模型路径"""
    return os.path.join(models_dir, f'{model_name}_model.joblib')

def validate_input_data(data, required_features):
    """验证输入数据是否包含所有必需的特征"""
    missing_features = [feature for feature in required_features if feature not in data]
    if missing_features:
        logger.error(f"缺少必需的特征: {missing_features}")
        return False
    return True

def map_smoking_status(smoking_status):
    """映射吸烟状态到数值"""
    mapping = {'never': 0, 'former': 1, 'current': 2}
    return mapping.get(smoking_status, 0)

def map_gender(gender):
    """映射性别到数值"""
    return 1 if gender == 'female' else 0

def map_mutation(mutation):
    """映射突变状态到数值"""
    return 1 if mutation == 'positive' else 0
