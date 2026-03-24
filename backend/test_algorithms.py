import pandas as pd
import joblib
import os
import logging
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    precision_recall_curve, roc_curve
)
import matplotlib.pyplot as plt
import numpy as np

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AlgorithmTester:
    def __init__(self, data_path='data/cancer_data.csv', models_dir='models'):
        """
        算法测试器初始化
        
        Args:
            data_path: 测试数据路径
            models_dir: 模型存储目录
        """
        self.data_path = data_path
        self.models_dir = models_dir
        self.models = {}
        self.data = None
        self.X = None
        self.y = None
        
        # 加载测试数据
        self._load_data()
        
        # 加载所有训练好的模型
        self._load_models()
    
    def _load_data(self):
        """加载测试数据"""
        logger.info(f"加载测试数据: {self.data_path}")
        self.data = pd.read_csv(self.data_path)
        self.X = self.data.drop('risk', axis=1)
        self.y = self.data['risk']
        logger.info(f"测试数据加载完成，共{len(self.data)}个样本")
    
    def _load_models(self):
        """加载所有训练好的模型"""
        logger.info(f"从{self.models_dir}加载模型...")
        
        # 获取所有模型文件
        model_files = [f for f in os.listdir(self.models_dir) if f.endswith('_model.joblib')]
        
        for model_file in model_files:
            model_name = model_file.replace('_model.joblib', '')
            model_path = os.path.join(self.models_dir, model_file)
            
            try:
                self.models[model_name] = joblib.load(model_path)
                logger.info(f"成功加载模型: {model_name}")
            except Exception as e:
                logger.error(f"加载模型{model_name}失败: {str(e)}")
        
        logger.info(f"共加载{len(self.models)}个模型")
    
    def test_single_model(self, model_name, save_report=False):
        """
        测试单个模型
        
        Args:
            model_name: 模型名称
            save_report: 是否保存测试报告
        
        Returns:
            测试结果字典
        """
        if model_name not in self.models:
            logger.error(f"模型{model_name}不存在")
            return None
        
        logger.info(f"开始测试模型: {model_name}")
        model = self.models[model_name]
        
        # 预测
        y_pred = model.predict(self.X)
        y_pred_proba = model.predict_proba(self.X) if hasattr(model, 'predict_proba') else None
        
        # 计算评估指标
        results = {
            'model_name': model_name,
            'accuracy': accuracy_score(self.y, y_pred),
            'precision': precision_score(self.y, y_pred, average='weighted'),
            'recall': recall_score(self.y, y_pred, average='weighted'),
            'f1_score': f1_score(self.y, y_pred, average='weighted'),
            'confusion_matrix': confusion_matrix(self.y, y_pred).tolist(),
            'classification_report': classification_report(self.y, y_pred, output_dict=True)
        }
        
        # 如果模型支持概率预测，计算ROC和AUC
        if y_pred_proba is not None:
            try:
                # 多分类情况下的AUC计算
                roc_auc = roc_auc_score(self.y, y_pred_proba, multi_class='ovo', average='weighted')
                results['roc_auc'] = roc_auc
            except Exception as e:
                logger.warning(f"计算{model_name}的ROC AUC失败: {str(e)}")
        
        # 打印结果
        self._print_test_results(results)
        
        # 保存报告
        if save_report:
            self._save_test_report(results)
        
        return results
    
    def test_all_models(self, save_report=False):
        """
        测试所有模型
        
        Args:
            save_report: 是否保存测试报告
        
        Returns:
            所有模型的测试结果字典
        """
        logger.info("开始测试所有模型...")
        all_results = {}
        
        for model_name in self.models.keys():
            results = self.test_single_model(model_name, save_report)
            if results:
                all_results[model_name] = results
        
        # 比较所有模型
        self._compare_models(all_results)
        
        return all_results
    
    def _print_test_results(self, results):
        """
        打印测试结果
        
        Args:
            results: 测试结果字典
        """
        model_name = results['model_name']
        
        logger.info(f"\n=== {model_name} 测试结果 ===")
        logger.info(f"准确率: {results['accuracy']:.4f}")
        logger.info(f"精确率: {results['precision']:.4f}")
        logger.info(f"召回率: {results['recall']:.4f}")
        logger.info(f"F1分数: {results['f1_score']:.4f}")
        
        if 'roc_auc' in results:
            logger.info(f"ROC AUC: {results['roc_auc']:.4f}")
        
        logger.info(f"混淆矩阵:")
        for row in results['confusion_matrix']:
            logger.info(row)
        
        logger.info(f"分类报告:")
        for class_name, metrics in results['classification_report'].items():
            if isinstance(metrics, dict):
                logger.info(f"类别 {class_name}: 精度={metrics['precision']:.4f}, 召回率={metrics['recall']:.4f}, F1={metrics['f1-score']:.4f}, 支持数={metrics['support']}")
    
    def _save_test_report(self, results):
        """
        保存测试报告到文件
        
        Args:
            results: 测试结果字典
        """
        model_name = results['model_name']
        report_path = f"reports/{model_name}_test_report.txt"
        
        # 创建报告目录
        os.makedirs('reports', exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"=== {model_name} 测试报告 ===\n\n")
            f.write(f"测试时间: {pd.Timestamp.now()}\n\n")
            
            f.write("1. 基本指标\n")
            f.write(f"准确率: {results['accuracy']:.4f}\n")
            f.write(f"精确率: {results['precision']:.4f}\n")
            f.write(f"召回率: {results['recall']:.4f}\n")
            f.write(f"F1分数: {results['f1_score']:.4f}\n")
            
            if 'roc_auc' in results:
                f.write(f"ROC AUC: {results['roc_auc']:.4f}\n")
            
            f.write("\n2. 混淆矩阵\n")
            for row in results['confusion_matrix']:
                f.write(' '.join(map(str, row)) + '\n')
            
            f.write("\n3. 分类报告\n")
            for class_name, metrics in results['classification_report'].items():
                if isinstance(metrics, dict):
                    f.write(f"类别 {class_name}: 精度={metrics['precision']:.4f}, 召回率={metrics['recall']:.4f}, F1={metrics['f1-score']:.4f}, 支持数={metrics['support']}\n")
        
        logger.info(f"测试报告已保存到: {report_path}")
    
    def _compare_models(self, all_results):
        """
        比较所有模型的性能
        
        Args:
            all_results: 所有模型的测试结果字典
        """
        logger.info("\n=== 模型性能比较 ===")
        
        # 创建比较表格
        compare_table = "模型名称 | 准确率 | 精确率 | 召回率 | F1分数 | ROC AUC\n"
        compare_table += "-" * 70 + "\n"
        
        for model_name, results in all_results.items():
            roc_auc = results.get('roc_auc', 'N/A')
            if isinstance(roc_auc, float):
                roc_auc = f"{roc_auc:.4f}"
            
            compare_table += f"{model_name:<10} | {results['accuracy']:<.4f} | {results['precision']:<.4f} | {results['recall']:<.4f} | {results['f1_score']:<.4f} | {roc_auc:<6}\n"
        
        logger.info(compare_table)
        
        # 保存比较结果
        with open('reports/models_comparison.txt', 'w', encoding='utf-8') as f:
            f.write(f"=== 模型性能比较报告 ===\n\n")
            f.write(f"生成时间: {pd.Timestamp.now()}\n\n")
            f.write(compare_table)
        
        logger.info("模型比较结果已保存到: reports/models_comparison.txt")
    
    def predict_single_sample(self, model_name, sample):
        """
        使用单个模型预测单个样本
        
        Args:
            model_name: 模型名称
            sample: 样本数据，可以是字典或DataFrame
        
        Returns:
            预测结果
        """
        if model_name not in self.models:
            logger.error(f"模型{model_name}不存在")
            return None
        
        model = self.models[model_name]
        
        # 转换样本为DataFrame
        if isinstance(sample, dict):
            sample_df = pd.DataFrame([sample])
        elif isinstance(sample, pd.DataFrame):
            sample_df = sample
        else:
            logger.error("样本数据类型不支持，必须是字典或DataFrame")
            return None
        
        # 确保样本特征与模型训练时一致
        expected_features = self.X.columns.tolist()
        sample_df = sample_df[expected_features]
        
        # 预测
        prediction = model.predict(sample_df)[0]
        probabilities = model.predict_proba(sample_df)[0] if hasattr(model, 'predict_proba') else None
        
        result = {
            'model_name': model_name,
            'prediction': int(prediction),
            'risk_level': ['low', 'medium', 'high'][int(prediction)]
        }
        
        if probabilities is not None:
            result['probabilities'] = {
                'low': float(probabilities[0]),
                'medium': float(probabilities[1]),
                'high': float(probabilities[2])
            }
            result['confidence'] = float(max(probabilities))
        
        return result
    
    def predict_single_sample_all_models(self, sample):
        """
        使用所有模型预测单个样本
        
        Args:
            sample: 样本数据，可以是字典或DataFrame
        
        Returns:
            所有模型的预测结果列表
        """
        logger.info("使用所有模型预测单个样本...")
        
        predictions = []
        for model_name in self.models.keys():
            result = self.predict_single_sample(model_name, sample)
            if result:
                predictions.append(result)
        
        return predictions

if __name__ == "__main__":
    # 测试所有模型
    tester = AlgorithmTester()
    
    # 测试单个模型
    # tester.test_single_model('random_forest', save_report=True)
    
    # 测试所有模型并生成报告
    tester.test_all_models(save_report=True)
    
    # 测试单样本预测
    logger.info("\n=== 单样本预测测试 ===")
    sample = {
        'age': 60,
        'gender': 1,
        'bmi': 28.5,
        'smoking': 2,
        'tumor_marker1': 150.5,
        'tumor_marker2': 60.2,
        'mutation': 1
    }
    
    predictions = tester.predict_single_sample_all_models(sample)
    for pred in predictions:
        logger.info(f"模型{pred['model_name']}预测结果: {pred['risk_level']}")
        if 'confidence' in pred:
            logger.info(f"置信度: {pred['confidence']:.4f}")
            logger.info(f"概率分布: {pred['probabilities']}")
        logger.info("---")
