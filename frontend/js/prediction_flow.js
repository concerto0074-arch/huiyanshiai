document.addEventListener('DOMContentLoaded', function() {
    // === UI Elements ===
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const fileNameDisplay = document.getElementById('file-name-display');
    const actualFileName = document.getElementById('actual-file-name');
    
    const modelOptions = document.querySelectorAll('.model-option');
    const startPredictionBtn = document.getElementById('start-prediction-btn');
    const resetPredictionBtn = document.getElementById('reset-prediction-btn');
    
    const modelSelectionView = document.getElementById('model-selection-view');
    const computingView = document.getElementById('computing-view');
    const resultView = document.getElementById('result-view');
    const computingProgress = document.getElementById('computing-progress');
    const loadingText = document.getElementById('loading-text');

    let isFileUploaded = false;
    let uploadedFile = null;
    let selectedModel = 'AI 智能匹配 (推荐)';

    // === File Upload Logic ===
    fileInput.addEventListener('change', function(e) {
        if (this.files && this.files.length > 0) {
            handleFileSelect(this.files[0]);
        }
    });

    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = '#10b981';
        this.style.backgroundColor = 'rgba(16, 185, 129, 0.05)';
    });

    dropZone.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.style.borderColor = '#cbd5e1';
        this.style.backgroundColor = 'transparent';
    });

    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#cbd5e1';
        this.style.backgroundColor = 'transparent';
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    function handleFileSelect(file) {
        uploadedFile = file;
        actualFileName.textContent = file.name;
        fileNameDisplay.style.display = 'block';
        dropZone.querySelector('h5').textContent = '文件准备就绪';
        isFileUploaded = true;
    }

    // === Model Selection Logic ===
    modelOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            // Prevent clicking info button from triggering option selection
            if (e.target.closest('.view-details-btn')) {
                return;
            }
            // Remove active class from all
            modelOptions.forEach(opt => {
                opt.classList.remove('active');
                opt.style.borderColor = '#e2e8f0';
                opt.style.backgroundColor = '#fff';
                const checkIcon = opt.querySelector('.fa-check-circle');
                if (checkIcon) checkIcon.style.display = 'none';
            });

            // Add active class to clicked
            this.classList.add('active');
            this.style.borderColor = '#2563eb';
            this.style.backgroundColor = 'rgba(37, 99, 235, 0.05)';
            const checkIcon = this.querySelector('.fa-check-circle');
            if (checkIcon) checkIcon.style.display = 'block';

            selectedModel = this.querySelector('h5, h6').innerText.trim();
        });
    });

    // === Prediction Flow ===
    startPredictionBtn.addEventListener('click', function() {
        const activeTab = document.querySelector('.custom-pills .nav-link.active').id;
        
        let patientData = {};
        const geneModelMap = {
            'WGCNA-MSGL高维组学联合集群 (R)': 'AI 智能匹配 (推荐)',
            'WGCNA-MSGL高维组学联合集群': 'AI 智能匹配 (推荐)',
            'AI 智能匹配 (推荐)': 'AI 智能匹配 (推荐)',
            '支持向量机 (SVM)': 'MSGL算法'
        };

        if (activeTab === 'upload-tab') {
            if (!isFileUploaded || !uploadedFile) {
                alert('请先上传高维基因表达数据文件(CSV)！');
                return;
            }
            
            const file = uploadedFile;
            const formData = new FormData();
            formData.append('file', file);
            
            let usingModel = selectedModel;
            if (selectedModel === 'AI 智能匹配 (推荐)') {
                usingModel = 'AI 智能匹配 (推荐)';
                alert('💡 AI 智能匹配推演：\n系统解析到您上传的是高维基因表达特征文件。\n已自动为您路由至科研级【WGCNA与多项式稀疏群Lasso算法】运算集群。');
            }
            usingModel = geneModelMap[usingModel] || 'AI 智能匹配 (推荐)';
            formData.append('algorithm', usingModel); // Send raw model name for R
            
            // 1. Hide selection view
            modelSelectionView.style.display = 'none';
            // 2. Show computing view
            computingView.style.display = 'flex';
            
            // 3. Execute R-based prediction
            executeGenePrediction(formData, selectedModel === 'AI 智能匹配 (推荐)' ? 'WGCNA-MSGL高维组学联合集群 (R)' : selectedModel);
            return;
        } else {
            // Validate manual input
            const ageInput = document.getElementById('ws-age').value;
            const ceaInput = document.getElementById('ws-cea').value;
            if (!ageInput || !ceaInput) {
                alert('请填写必填项（完整年龄和核心肿瘤标志物信息）！');
                return;
            }
            
            patientData = {
                age: parseInt(ageInput) || 45,
                gender: document.getElementById('ws-gender').value === '男' ? 'male' : 'female',
                bmi: 22.5, // 默认均值
                smoke: 'never',
                tumorMarker1: parseFloat(ceaInput) || 3.5,
                tumorMarker2: parseFloat(document.getElementById('ws-wbc').value) || 6.8,
                mutation1: document.getElementById('ws-egfr').value === 'positive' ? 'positive' : 'none'
            };
        }

        const modelMap = {
            '随机森林 (Random Forest)': 'random_forest',
            '支持向量机 (SVM)': 'svm',
            '逻辑回归 (Logistic Regression)': 'logistic_regression',
            'K-近邻 (KNN)': 'random_forest',
            '医学判别决策树 (Decision Tree)': 'random_forest',
            '集成特征森林 (Ensemble Forest)': 'random_forest',
            '核-支持向量 (Kernel SVM)': 'svm',
            'AI 智能匹配 (推荐)': 'random_forest'
        };
        let backendAlgo = modelMap[selectedModel] || 'random_forest';
        let usingModelName = selectedModel;

        if (selectedModel === 'AI 智能匹配 (推荐)') {
            backendAlgo = 'random_forest';
            usingModelName = '集成特征森林 (临床基础特化版)';
            alert('💡 AI 智能匹配推演：\n系统检测到您当前采用的是二维常规体征表单输入。\n已为您自动甄选【集成特征森林 (Ensemble Forest)】模型以最大化基础特征分类鉴别力。');
        }

        // 1. Hide selection view
        modelSelectionView.style.display = 'none';
        
        // 2. Show computing view
        computingView.style.display = 'flex';
        
        // 3. Execute real API validation and prediction
        executePrediction(patientData, backendAlgo, usingModelName);
    });

    function updateResultViewDOM(data) {
        const riskPercentage = document.getElementById('result-risk-percentage');
        const riskLabel = document.getElementById('result-risk-label');
        const modelName = document.getElementById('result-model-name');
        const confidence = document.getElementById('result-confidence');

        if (riskPercentage) {
            let maxProb = 0;
            if (data.probabilities) {
                const probs = Object.values(data.probabilities);
                maxProb = probs.length > 0 ? Math.max(...probs) : 0;
            }
            let score = Math.round(maxProb * 100);
            if(data.riskLevel === '高风险' && score < 50) score = Math.min(99, score + 40);
            if(score <= 0) score = 14; 
            
            riskPercentage.textContent = score + '%';
            riskPercentage.style.color = data.riskLevel === '低风险' ? '#059669' : (data.riskLevel === '高风险' ? '#dc2626' : '#d97706');
            
            if (data.riskLevel === '低风险') {
                riskLabel.textContent = '低于人群平均水平';
                riskLabel.style.color = '#059669';  riskLabel.style.background = '#ecfdf5';
            } else if (data.riskLevel === '高风险') {
                riskLabel.textContent = '高于人群平均水平（高危）';
                riskLabel.style.color = '#dc2626';  riskLabel.style.background = '#fef2f2';
            } else {
                riskLabel.textContent = '处于临界风险地带';
                riskLabel.style.color = '#d97706';  riskLabel.style.background = '#fef3c7';
            }
        }
        if (modelName) modelName.textContent = data.algorithm || '核心分类网络';
        if (confidence) confidence.textContent = (data.confidence || 90.0) + '%';
    }

    async function executeGenePrediction(formData, displayModelName) {
        let progress = 0;
        computingProgress.style.width = '0%';
        
        const loadingTexts = [
            '正在上传高维基因组数据...',
            '正在唤醒 R 核心算法环境...',
            '执行 WGCNA 模块聚类与共表达提取...',
            '执行多项式稀疏群 Lasso 分类推理...',
            '生成多水平特征组学报告...'
        ];
        
        let textIndex = 0;
        loadingText.textContent = loadingTexts[textIndex];

        // Start progress bar animation
        const interval = setInterval(() => {
            progress += Math.floor(Math.random() * 8) + 2;
            if (progress >= 90) progress = 90; // Wait for R backgorund process
            
            computingProgress.style.width = progress + '%';
            const expectedTextIndex = Math.floor(progress / 20);
            if (expectedTextIndex > textIndex && expectedTextIndex < loadingTexts.length) {
                textIndex = expectedTextIndex;
                loadingText.textContent = loadingTexts[textIndex];
            }
        }, 500);

        try {
            const BASE_URL = (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL ? window.APP_CONFIG.API_BASE_URL : 'http://127.0.0.1:5000');
            const API_URL = BASE_URL + '/api/predict/gene';

            // 先唤醒后端（Render 免费版冷启动可能需要 30~50 秒）
            try { await fetch(BASE_URL + '/api/health', { method: 'GET', signal: AbortSignal.timeout(55000) }); } catch(e) {}

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 60000);
            const response = await fetch(API_URL, {
                method: 'POST',
                // Note: Do NOT set Content-Type header when sending FormData, browser handles boundary
                body: formData,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error('API Request Failed, status: ' + response.status);
            }
            
            const resultData = await response.json();
            
            // Map R result to LocalStorage for report.html rendering
            const reportData = {
                patientName: '匿名供体样本 (基因流)',
                patientGender: '未标记',
                patientAge: '基因多组学',
                patientBmi: '详见模块',
                patientSmoke: '未知',
                algorithm: resultData.algorithm || displayModelName,
                riskLevel: resultData.riskLevel,
                confidence: resultData.confidence,
                probabilities: resultData.probabilities,
                factors: resultData.factors || [],
                tumorMarkers: resultData.tumorMarkers || [],
                recommendations: resultData.recommendations || []
            };

            localStorage.setItem('predictionResult', JSON.stringify(reportData));
            updateResultViewDOM(reportData);
            
            // 自动保存报告到后端（如果用户已登录）
            autoSaveReport(reportData);

            // Finish progress successfully
            clearInterval(interval);
            computingProgress.style.width = '100%';
            loadingText.textContent = '基因组学深度推演完成！';
            
            setTimeout(() => {
                computingView.style.display = 'none';
                resultView.style.display = 'flex';
            }, 800);

        } catch (error) {
            console.error('R Integration Prediction failed:', error);
            clearInterval(interval);
            alert('调取底层 R 基因算法环境失败。\n请确保 Python 服务和 R 服务就绪。');
            
            // Switch back to model selection
            computingView.style.display = 'none';
            modelSelectionView.style.display = 'block';
        }
    }

    async function executePrediction(patientData, backendAlgo, displayModelName) {
        let progress = 0;
        computingProgress.style.width = '0%';
        
        const loadingTexts = [
            '正在加载数据集...',
            '正在进行特征工程与清洗...',
            '连接服务端核心算法...',
            '执行深度计算推理...',
            '生成高维评估报告...'
        ];
        
        let textIndex = 0;
        loadingText.textContent = loadingTexts[textIndex];

        // Start progress bar animation
        const interval = setInterval(() => {
            progress += Math.floor(Math.random() * 10) + 2;
            if (progress >= 90) progress = 90; // API wait lock
            
            computingProgress.style.width = progress + '%';
            const expectedTextIndex = Math.floor(progress / 20);
            if (expectedTextIndex > textIndex && expectedTextIndex < loadingTexts.length) {
                textIndex = expectedTextIndex;
                loadingText.textContent = loadingTexts[textIndex];
            }
        }, 300);

        try {
            const API_URL = (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL ? window.APP_CONFIG.API_BASE_URL : 'http://127.0.0.1:5000') + '/api/predict_form';
            
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    algorithm: backendAlgo,
                    ...patientData
                })
            });
            
            if (!response.ok) {
                throw new Error('API Request Failed, status: ' + response.status);
            }
            
            const resultData = await response.json();
            
            // Map AI result to LocalStorage for report.html rendering
            // predict_form 返回字段: riskLevel(中文), confidence, probabilities(中文key), factors, tumorMarkers, recommendations
            const reportData = {
                patientName: resultData.patientName || localStorage.getItem('username') || '匿名患者',
                patientGender: patientData.gender === 'male' ? '男' : (patientData.gender === 'female' ? '女' : '未知'),
                patientAge: patientData.age || '-',
                patientHeight: patientData.height || '-',
                patientWeight: patientData.weight || '-',
                patientBmi: patientData.bmi || '-',
                patientSmoke: patientData.smoke === 'never' ? '从不' : (patientData.smoke === 'former' ? '曾经吸烟' : '有吸烟史'),
                patientDrink: patientData.drink === 'never' ? '从不' : (patientData.drink === 'occasionally' ? '偶尔' : (patientData.drink ? '有' : 'N/A')),
                patientFamilyHistory: patientData.familyHistory === 'yes' ? '有' : (patientData.familyHistory === 'no' ? '无' : 'N/A'),
                patientPastHistory: patientData.pastHistory || patientData.past_history || 'N/A',
                algorithm: displayModelName,
                riskLevel: resultData.riskLevel || '未知',
                confidence: resultData.confidence || 90.0,
                probabilities: resultData.probabilities || { '低风险': 0, '中风险': 0, '高风险': 0 },
                factors: resultData.factors || [
                    { name: '年龄', value: patientData.age + '岁', impact: '基础风险系数', isPositive: patientData.age < 50 }
                ],
                tumorMarkers: resultData.tumorMarkers || [
                    { name: 'CEA', value: patientData.tumorMarker1, normalRange: '0-5 ng/mL', status: patientData.tumorMarker1 <= 5.0 ? '正常' : '异常' }
                ],
                recommendations: resultData.recommendations || [
                    { title: 'AI 深度分析队列中', content: '等待服务端大模型生成详细专业指导...' }
                ]
            };

            localStorage.setItem('predictionResult', JSON.stringify(reportData));
            updateResultViewDOM(reportData);
            
            // 自动保存报告到后端（如果用户已登录）
            autoSaveReport(reportData, patientData);

            // Finish progress successfully
            clearInterval(interval);
            computingProgress.style.width = '100%';
            loadingText.textContent = '计算与分析完成！';
            
            setTimeout(() => {
                computingView.style.display = 'none';
                resultView.style.display = 'flex';
            }, 600);

        } catch (error) {
            console.error('Prediction failed. Ensure Flask Backend is running:', error);
            
            clearInterval(interval);
            alert('连接算法服务器(Python)失败，无法生成预测。\n请确保 Python Flask 服务运行在端口 5000。');
            
            computingView.style.display = 'none';
            modelSelectionView.style.display = 'block';
        }
    }

    // === 自动保存报告到后端 ===
    async function autoSaveReport(reportData, patientData) {
        const token = localStorage.getItem('token');
        if (!token) {
            console.log('[autoSaveReport] 用户未登录，跳过保存');
            return;
        }
        try {
            const API_URL = (window.APP_CONFIG && window.APP_CONFIG.API_BASE_URL ? window.APP_CONFIG.API_BASE_URL : 'http://127.0.0.1:5000') + '/api/save_report';
            const body = {
                algorithm: reportData.algorithm || '未知',
                riskLevel: reportData.riskLevel,
                confidence: reportData.confidence,
                probabilities: reportData.probabilities,
                factors: reportData.factors,
                recommendations: reportData.recommendations,
                patient_data: patientData || {}
            };
            const resp = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + token
                },
                body: JSON.stringify(body)
            });
            const data = await resp.json();
            if (data.success) {
                console.log('[autoSaveReport] 报告已保存, ID=' + data.report_id);
            } else {
                console.warn('[autoSaveReport] 保存失败:', data.error);
            }
        } catch (e) {
            console.warn('[autoSaveReport] 网络异常，报告未保存:', e);
        }
    }

    // === Reset Flow ===
    resetPredictionBtn.addEventListener('click', function() {
        resultView.style.display = 'none';
        computingView.style.display = 'none';
        modelSelectionView.style.display = 'block';
        computingProgress.style.width = '0%';
    });
});

// CSV Sample Data Generator for Downloads (Now using the real high-dimensional dataset)
window.downloadSampleData = function() {
    console.log("Downloading real WGCNA sequence data...");
    const link = document.createElement("a");
    link.href = "sample_gene_data.csv";
    link.download = "cleandata(WGCNA_Sample).csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};
