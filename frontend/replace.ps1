# 读取原始文件内容
$content = Get-Content -Path "cases.html" -Raw -Encoding UTF8

# 读取新的登录模态框内容
$newLoginContent = Get-Content -Path "new_login_content.txt" -Raw -Encoding UTF8

# 查找登录模态框的开始位置
$loginStart = $content.IndexOf('<!-- 登录模态框 -->')
if ($loginStart -eq -1) {
    Write-Output "找不到登录模态框的开始位置！"
    exit 1
}

# 查找登录模态框的结束位置（通过查找注册模态框的开始）
$registerStart = $content.IndexOf('<!-- 注册模态框 -->', $loginStart)
if ($registerStart -eq -1) {
    Write-Output "找不到注册模态框的开始位置！"
    exit 1
}

# 构建新的文件内容
$newContent = $content.Substring(0, $loginStart) + $newLoginContent + $content.Substring($registerStart)

# 保存更新后的内容
Set-Content -Path "cases.html" -Value $newContent -Encoding UTF8

Write-Output "登录模态框已成功更新！"
