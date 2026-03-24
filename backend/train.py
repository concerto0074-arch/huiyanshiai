import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import logging

from config import (
    DATA_PATH, TRAIN_TEST_SPLIT, RANDOM_STATE, MODELS_DIR, 
    MODEL_SUFFIX, RESULTS_FILE, ALGORITHMS, hyperparameters
)
from utils import (
    load_data, save_model, save_results, ensure_dir, setup_logging
)

# 设置日志
logger = setup_logging()

def main():
    """主函数"""
    # 加载数据
    df = load_data(DATA_PATH)
    
    # 特征和标签
    X = df.drop('risk', axis=1)
    y = df['risk']
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TRAIN_TEST_SPLIT, random_state=RANDOM_STATE
    )
    logger.info(f"数据集划分完成，训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
    
    # 定义模型列表
    models = {
        'random_forest': Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestClassifier(random_state=RANDOM_STATE))
        ]),
        'svm': Pipeline([
            ('scaler', StandardScaler()),
            ('model', SVC(probability=True, random_state=RANDOM_STATE))
        ]),
        'logistic_regression': Pipeline([
            ('scaler', StandardScaler()),
            ('model', LogisticRegression(random_state=RANDOM_STATE))
        ])
    }
    
    # 训练并保存模型
    results = {}
    
    # 确保模型目录存在
    ensure_dir(MODELS_DIR)
    
    for name in ALGORITHMS:
        if name not in models:
            logger.warning(f"模型{name}未定义，跳过")
            continue
        
        model = models[name]
        logger.info(f"开始训练{name}模型...")
        
        # 执行K折交叉验证
        logger.info(f"执行5折交叉验证...")
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        logger.info(f"{name}交叉验证准确率: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        
        # 执行网格搜索优化超参数
        logger.info(f"执行超参数网格搜索...")
        grid_search = GridSearchCV(
            estimator=model, 
            param_grid=hyperparameters[name], 
            cv=5, 
            scoring='accuracy', 
            n_jobs=-1
        )
        grid_search.fit(X_train, y_train)
        
        logger.info(f"{name}最佳参数: {grid_search.best_params_}")
        logger.info(f"{name}最佳交叉验证准确率: {grid_search.best_score_:.4f}")
        
        # 使用最佳模型进行测试
        best_model = grid_search.best_estimator_
        y_pred = best_model.predict(X_test)
        
        # 评估模型
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"{name}测试集准确率: {accuracy:.4f}")
        logger.info(f"{name}分类报告:")
        logger.info(classification_report(y_test, y_pred))
        logger.info(f"{name}混淆矩阵:")
        logger.info(confusion_matrix(y_test, y_pred))
        
        # 保存最佳模型
        model_path = f'{MODELS_DIR}/{name}{MODEL_SUFFIX}'
        save_model(best_model, model_path)
        
        # 保存结果
        results[name] = {
            'cv_scores': cv_scores,
            'best_params': grid_search.best_params_,
            'best_cv_score': grid_search.best_score_,
            'test_accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
    
    # 保存所有结果
    results_path = f'{MODELS_DIR}/{RESULTS_FILE}'
    save_results(results, results_path)
    logger.info(f"所有模型训练完成，结果已保存到 {results_path}")
    
    # 打印模型比较结果
    logger.info("\n=== 模型比较结果 ===")
    for name, result in results.items():
        logger.info(f"{name}: 交叉验证准确率={result['best_cv_score']:.4f}, 测试集准确率={result['test_accuracy']:.4f}")

if __name__ == "__main__":
    main()