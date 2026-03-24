const fs = require('fs');
const path = require('path');

// 读取article-detail.html的内容作为模板
const templatePath = path.join(__dirname, 'article-detail.html');
const templateContent = fs.readFileSync(templatePath, 'utf8');

// 提取需要替换的部分
const loginModalMatch = templateContent.match(/<!-- 登录模态框 -->[\s\S]*?<!-- 注册模态框 -->[\s\S]*?<!-- 用户信息模态框 -->/);
const loginModalContent = loginModalMatch ? loginModalMatch[0] : '';

const jsFunctionsMatch = templateContent.match(/\/\/ 登录\/注册相关函数[\s\S]*?\/\/ 根据URL参数加载文章内容/);
const jsFunctionsContent = jsFunctionsMatch ? jsFunctionsMatch[0] : '';

// 获取所有article-detail*.html文件
const articleDetailFiles = fs.readdirSync(__dirname)
    .filter(file => file.match(/article-detail-\d+\.html$/))
    .map(file => path.join(__dirname, file));

// 遍历所有文件并更新
articleDetailFiles.forEach(file => {
    console.log(`正在更新 ${file}...`);
    let content = fs.readFileSync(file, 'utf8');
    
    // 替换登录/注册模态框部分
    content = content.replace(/<!-- 登录\/注册模态框 -->[\s\S]*?<!-- 用户信息模态框 -->/, loginModalContent);
    
    // 替换JavaScript函数部分
    content = content.replace(/\/\/ 登录\/注册相关函数[\s\S]*?\/\/ 根据URL参数加载文章内容/, jsFunctionsContent);
    
    // 保存修改后的文件
    fs.writeFileSync(file, content, 'utf8');
    console.log(`已更新 ${file}`);
});

console.log('所有article-detail*.html页面已更新完成！');