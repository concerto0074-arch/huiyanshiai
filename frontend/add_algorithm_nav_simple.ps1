# 定义要修改的文件模式
$filePattern = "article-detail*.html"

# 定义要查找的字符串
$searchString = '<li class="nav-item">
                        <a class="nav-link" href="group.html">团体方案</a>
                    </li>'

# 定义要替换的字符串
$replaceString = '<li class="nav-item">
                        <a class="nav-link" href="group.html">团体方案</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="algorithms.html">核心算法</a>
                    </li>'

# 获取所有匹配的文件
$files = Get-ChildItem -Path . -Filter $filePattern

# 遍历每个文件
foreach ($file in $files) {
    Write-Host "Processing file: $($file.Name)"
    
    # 读取文件内容
    $content = Get-Content -Path $file.FullName -Raw
    
    # 检查文件中是否包含要查找的字符串
    if ($content -like "*$searchString*") {
        # 替换字符串
        $newContent = $content -replace [regex]::Escape($searchString), $replaceString
        
        # 写入修改后的内容
        Set-Content -Path $file.FullName -Value $newContent -Encoding UTF8
        
        Write-Host "Successfully modified: $($file.Name)"
    } else {
        Write-Host "Search string not found in: $($file.Name)"
    }
}

Write-Host "All files processed."