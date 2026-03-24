# 读取article-detail.html作为模板
$templatePath = Join-Path $PSScriptRoot "article-detail.html"
$templateContent = Get-Content -Path $templatePath -Encoding UTF8

# 提取登录模态框开始和结束位置
$loginModalStart = ($templateContent | Select-String -Pattern "<!-- 登录模态框 -->" -CaseSensitive).LineNumber - 1
$userInfoModalStart = ($templateContent | Select-String -Pattern "<!-- 用户信息模态框 -->" -CaseSensitive).LineNumber - 1

# 提取登录模态框内容
$loginModalContent = $templateContent[$loginModalStart..$userInfoModalStart] -join "`n"

# 提取JavaScript函数开始和结束位置
$jsFunctionsStart = ($templateContent | Select-String -Pattern "// 登录/注册相关函数" -CaseSensitive).LineNumber - 1
$pageLoadStart = ($templateContent | Select-String -Pattern "// 页面加载完成后执行" -CaseSensitive).LineNumber - 1

# 提取JavaScript函数内容
$jsFunctionsContent = $templateContent[$jsFunctionsStart..($pageLoadStart-1)] -join "`n"

# 获取所有article-detail*.html文件
$articleDetailFiles = Get-ChildItem -Path $PSScriptRoot -Filter "article-detail-*.html"

# 遍历所有文件并更新
foreach ($file in $articleDetailFiles) {
    Write-Host "正在更新 $($file.Name)..."
    $content = Get-Content -Path $file.FullName -Encoding UTF8
    
    # 找到当前文件中的登录模态框和JavaScript函数位置
    $currentLoginModalStart = ($content | Select-String -Pattern "<!-- 登录/注册模态框 -->" -CaseSensitive).LineNumber - 1
    $currentUserInfoModalStart = ($content | Select-String -Pattern "<!-- 用户信息模态框 -->" -CaseSensitive).LineNumber - 1
    $currentJsFunctionsStart = ($content | Select-String -Pattern "// 登录/注册相关函数" -CaseSensitive).LineNumber - 1
    $currentPageLoadStart = ($content | Select-String -Pattern "// 页面加载完成后执行" -CaseSensitive).LineNumber - 1
    
    if ($currentLoginModalStart -ne $null -and $currentUserInfoModalStart -ne $null -and $currentJsFunctionsStart -ne $null -and $currentPageLoadStart -ne $null) {
        # 替换登录模态框部分
        $newContent = $content[0..($currentLoginModalStart-1)] + $loginModalContent + $content[$currentUserInfoModalStart..($currentJsFunctionsStart-1)] + $jsFunctionsContent + $content[$currentPageLoadStart..($content.Length-1)]
        
        # 保存修改后的文件
        Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8
        Write-Host "已更新 $($file.Name)"
    } else {
        Write-Host "$($file.Name) 中的匹配模式不正确，跳过更新"
    }
}

Write-Host "所有article-detail*.html页面已更新完成！"