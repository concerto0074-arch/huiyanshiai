$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ProjectRoot 'backend'
$EnvFile = Join-Path $ProjectRoot '.env'
$PythonExe = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$RequiredModules = @('flask', 'flask_cors', 'pandas', 'numpy', 'requests', 'dotenv', 'bcrypt', 'jwt', 'joblib')

if (-not (Test-Path $EnvFile)) {
    Write-Host '[ERROR] .env file not found. Please create it from .env.example first.' -ForegroundColor Red
    exit 1
}

if (Test-Path $PythonExe) {
    $PythonCmd = $PythonExe
} else {
    $PythonCmd = 'python'
}

Write-Host '=== HuiYanShiAi Local Startup ===' -ForegroundColor Cyan
Write-Host "Project Root: $ProjectRoot"
Write-Host "Backend Dir: $BackendDir"
Write-Host "Python: $PythonCmd"

$envLines = Get-Content $EnvFile
$env:PORT = '5000'

$supabaseUrlLine = $envLines | Where-Object { $_ -match '^SUPABASE_URL=' } | Select-Object -First 1
$supabaseKeyLine = $envLines | Where-Object { $_ -match '^SUPABASE_ANON_KEY=' } | Select-Object -First 1
$jwtLine = $envLines | Where-Object { $_ -match '^JWT_SECRET=' } | Select-Object -First 1

$supabaseUrl = if ($supabaseUrlLine) { ($supabaseUrlLine -replace '^SUPABASE_URL=', '').Trim() } else { '' }
$supabaseKey = if ($supabaseKeyLine) { ($supabaseKeyLine -replace '^SUPABASE_ANON_KEY=', '').Trim() } else { '' }
$jwtSecret = if ($jwtLine) { ($jwtLine -replace '^JWT_SECRET=', '').Trim() } else { '' }

Write-Host "Local Port: $($env:PORT)"
Write-Host ("Supabase URL: " + $(if ($supabaseUrl) { 'configured' } else { 'missing' }))
Write-Host ("Supabase Key: " + $(if ($supabaseKey) { 'configured' } else { 'missing' }))
Write-Host ("JWT Secret: " + $(if ($jwtSecret) { 'configured' } else { 'missing' }))

Write-Host ''
Write-Host 'Open after startup:' -ForegroundColor Green
Write-Host "Home: http://127.0.0.1:$($env:PORT)/"
Write-Host "Algorithms: http://127.0.0.1:$($env:PORT)/algorithms.html"
Write-Host "System Status: http://127.0.0.1:$($env:PORT)/api/system-status"
Write-Host ''

$missingModules = @()
foreach ($module in $RequiredModules) {
    & $PythonCmd -c "import $module" 2>$null
    if ($LASTEXITCODE -ne 0) {
        $missingModules += $module
    }
}

if ($missingModules.Count -gt 0) {
    Write-Host '[ERROR] Missing Python modules detected:' -ForegroundColor Red
    $missingModules | ForEach-Object { Write-Host " - $_" -ForegroundColor Yellow }
    Write-Host ''
    Write-Host 'Install dependencies first:' -ForegroundColor Yellow
    Write-Host "  $PythonCmd -m pip install -r requirements.txt"
    exit 1
}

Set-Location $BackendDir
& $PythonCmd app.py
