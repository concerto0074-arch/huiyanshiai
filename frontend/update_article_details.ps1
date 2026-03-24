# 读取article-detail.html作为模板
$templatePath = Join-Path $PSScriptRoot "article-detail.html"
$templateContent = Get-Content -Path $templatePath -Raw

# 提取登录模态框部分
$loginModalPattern = '(?s)<!-- 登录模态框 -->.*?<!-- 用户信息模态框 -->'
$loginModalContent = [regex]::Match($templateContent, $loginModalPattern).Value

# 提取JavaScript函数部分
$jsFunctionsPattern = '(?s)// 登录/注册相关函数.*?// 根据URL参数加载文章内容'
$jsFunctionsContent = [regex]::Match($templateContent, $jsFunctionsPattern).Value

# 获取所有article-detail*.html文件
$articleDetailFiles = Get-ChildItem -Path $PSScriptRoot -Filter "article-detail-*.html"

# 遍历所有文件并更新
foreach ($file in $articleDetailFiles) {
    Write-Host "正在更新 $($file.Name)..."
    $content = Get-Content -Path $file.FullName -Raw
    
    # 替换登录/注册模态框部分
    $content = $content -replace $loginModalPattern, $loginModalContent
    
    # 替换JavaScript函数部分
    $content = $content -replace '(?s)// 登录/注册相关函数.*?// 页面加载完成后执行', $jsFunctionsContent
    
    # 保存修改后的文件
    Set-Content -Path $file.FullName -Value $content -Encoding UTF8
    Write-Host "已更新 $($file.Name)"
}

Write-Host "所有article-detail*.html页面已更新完成！"