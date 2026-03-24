# 定义要修改的文件模式
$filePattern = "article-detail*.html"

# 遍历所有匹配文件
foreach ($file in Get-ChildItem -Path . -Filter $filePattern) {
    Write-Host "Processing file: $($file.Name)"
    
    # 读取文件内容
    $content = Get-Content -Path $file.FullName -Encoding UTF8 -Raw
    
    # 定义要查找和替换的内容
    $searchText = "                    <li class="nav-item">
                        <a class="nav-link" href="group.html">团体方案</a>
                    </li>"
    $replaceText = "                    <li class="nav-item">
                        <a class="nav-link" href="group.html">团体方案</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="algorithms.html">核心算法</a>
                    </li>"
    
    # 查找并替换内容
    if ($content.Contains($searchText)) {
        $modifiedContent = $content.Replace($searchText, $replaceText)
        
        # 写入修改后的内容
        Set-Content -Path $file.FullName -Value $modifiedContent -Encoding UTF8
        
        Write-Host "Successfully modified: $($file.Name)"
    } else {
        Write-Host "Pattern not found in: $($file.Name)"
    }
}

Write-Host "All files have been processed successfully!"