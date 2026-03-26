# 配置文件

# 数据配置
DATA_PATH = 'data/cancer_data.csv'
TRAIN_TEST_SPLIT = 0.2
RANDOM_STATE = 42

# 模型配置
MODELS_DIR = 'models'
MODEL_SUFFIX = '_model.joblib'
RESULTS_FILE = 'training_results.joblib'

# 算法配置
ALGORITHMS = ['random_forest', 'svm', 'logistic_regression']

# 超参数配置
hyperparameters = {
    'random_forest': {
        'model__n_estimators': [50, 100, 200],
        'model__max_depth': [None, 10, 20],
        'model__min_samples_split': [2, 5, 10]
    },
    'svm': {
        'model__C': [0.1, 1, 10],
        'model__kernel': ['linear', 'rbf'],
        'model__gamma': ['scale', 'auto']
    },
    'logistic_regression': {
        'model__C': [0.1, 1, 10],
        'model__solver': ['liblinear', 'lbfgs']
    }
}

# 特征配置
FEATURES = {
    'age': '年龄',
    'gender': '性别',
    'bmi': 'BMI指数',
    'smoking': '吸烟史',
    'tumor_marker1': '肿瘤标志物1',
    'tumor_marker2': '肿瘤标志物2',
    'mutation': '基因突变'
}

# 模型描述
model_descriptions = {
    'random_forest': '基于集成学习的随机森林算法，通过多个决策树的投票进行分类，具有良好的泛化能力和抗过拟合能力',
    'svm': '支持向量机算法，通过寻找最优分类超平面实现分类，适合小样本、高维数据',
    'logistic_regression': '经典的线性分类算法，计算效率高，结果易解释',
    'xgboost': '基于梯度提升树的集成学习算法，具有高效、灵活、可扩展等特点，在各种机器学习竞赛中表现优异',
    'lightgbm': '基于梯度提升框架的分布式梯度提升树算法，训练速度快，内存占用小，精度高'
}

# API配置
API_HOST = '0.0.0.0'
API_PORT = 5001
API_DEBUG = False

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
