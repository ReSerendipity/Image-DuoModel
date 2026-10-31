#Requires -Version 5.1
# scripts/build_desktop_bundle.ps1
# 构建 Image MultiModel 桌面版「瘦包」发布资产（供 desktop/installer/setup.nsi 分发）。
#
# 目标形态（瘦包）：安装包 = 壳 + 应用代码 + 引导解释器（无 torch），
# 模型权重与 torch 都不进包，由程序内「下载管理」页（/downloads）按需安装。
#
# 数据卷解压后的布局（**四处必须对齐**，改动前先看这三处再动手）：
#   <InstallDir>\
#     ImageMultiModel.exe          壳（安装器用内嵌文件覆盖）
#     app\                         ← 后端 PROJECT_ROOT（config.yaml 在此）
#       integrated_app\...         应用包
#       config.yaml
#       version.json
#       downloads_catalog.json     下载清单（页面按它找环境包）
#       data\ logs\ outputs\       运行态目录
#     bootstrap\python.exe         ← 引导解释器（无 torch）
#     runtime\python.exe           ← 完整运行时（装完环境后才有；瘦包不含）
#
# 与下列三处对齐：
#   · desktop/src-tauri/src/python_process.rs::resolve_runtime_dir / detect_python_mode
#   · app/integrated_app/download_service.py::_runtime_dir
#   · 本脚本 $BootstrapDirName / $RuntimeDirName
#
# 用法：
#   .\scripts\build_desktop_bundle.ps1                            # 瘦包（默认）
#   .\scripts\build_desktop_bundle.ps1 -RuntimeDir D:\WPy64-31210 # 复用已备好的 WinPython（跳过下载）
#   .\scripts\build_desktop_bundle.ps1 -SkipDeps                  # 复用已装好依赖的解释器
#   .\scripts\build_desktop_bundle.ps1 -Mode runtime              # 只建 torch 环境包（zip 分卷 + 清单）
#   .\scripts\build_desktop_bundle.ps1 -Mode all                  # 两者都建（发版用）
#
# 产物（默认 dist\desktop-release\）：
#   ImageMultiModel-Data.7z.001..NNN  数据卷（app\ + bootstrap\）
#   ImageMultiModel-Runtime-cu128.zip.001..NNN  环境包（-Mode runtime/all）
#   downloads_catalog.json            下载清单
#   SHA256SUMS.txt / manifest.json / upload-list.txt

[CmdletBinding()]
param(
    [string]$Version = '',
    [string]$Root = '',
    [string]$OutDir = '',
    [string]$StagingDir = '',

    [ValidateSet('slim', 'runtime', 'all')][string]$Mode = 'slim',

    # 引导解释器：给 -RuntimeDir 时直接复用（目录须含 python.exe）；否则自动取 WinPython
    [string]$RuntimeDir = '',
    [string]$WinPythonUrl = 'https://github.com/winpython/winpython/releases/download/16.5.20250614/Winpython64-3.12.10.1dotb4.exe',

    # 环境包（torch）来源：本仓要求 cu128（RTX 50 系 sm_120，cu121 不支持）
    [string]$TorchIndexUrl = 'https://download.pytorch.org/whl/cu128',
    [string]$TorchVersion = '2.10.0',
    [string]$TorchvisionVersion = '0.25.0',

    # 分卷上限：支持 "1900MB" / "1.5GB" / 纯字节数；留空用默认 1900MB
    [string]$MaxPartBytes = '',
    [ValidateRange(0, 9)][int]$Level = 5,

    [switch]$SkipDeps,
    [switch]$SkipIncremental,
    [switch]$KeepStaging,
    [switch]$KeepArchive
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------- 常量 ----
$DataArchiveName = 'ImageMultiModel-Data.7z'
$PayloadAppName = 'app'
# 瘦包内置解释器目录名（无 torch）。环境装进去后目录名不变，只多出 torch——
# 与壳 python_process.rs 的 detect_python_mode 及后端 _runtime_dir() 三处必须一致。
$BootstrapDirName = 'bootstrap'
$RuntimeDirName = 'runtime'
$RuntimeZipName = 'ImageMultiModel-Runtime-cu128.zip'
$RuntimeDefaultTag = 'runtime-v1'
$CatalogFileName = 'downloads_catalog.json'
$ProductExe = 'ImageMultiModel.exe'
$ReleaseBase = 'https://github.com/ReSerendipity/Image-DuoModel/releases/download'

# 打包进 app\ 的项目内容（不含权重 / 运行时 / 开发产物）。
# 键 = 仓库内相对路径，值 = 装到 <payload>\app\ 下的相对路径。
$CodeDirs = [ordered]@{
    'app\integrated_app' = 'integrated_app'
    'comfy_kernel'       = 'comfy_kernel'
}
# version.json 由安装器写入 $INSTDIR 下的 app\ 目录（见 desktop/installer/setup.nsi），不在数据卷里重复一份
$CodeFiles = @('config.yaml', 'requirements.txt', 'README.md', 'LICENSE', 'NOTICE')
$ExcludeDirs = @('__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.git', 'node_modules',
    '.venv', 'venv', 'tests', 'data\cache', 'data\uploads', 'outputs', 'logs', 'dist', 'build')
$ExcludeFiles = @('*.pyc', '*.pyo', '*.log', '*.db', '*.db-wal', '*.db-shm', '*.bak', '.env', '*.pem', '*.key')

# ------------------------------------------------------------ 工具函数 ----
function Write-Step([string]$Text) {
    Write-Host ''
    Write-Host "== $Text" -ForegroundColor Cyan
}

function Find-SevenZip {
    $candidates = @(
        'C:\Program Files\7-Zip\7z.exe',
        'C:\Program Files (x86)\7-Zip\7z.exe',
        'C:\ProgramData\chocolatey\bin\7z.exe'
    )
    foreach ($c in $candidates) {
        if (Test-Path -LiteralPath $c) { return $c }
    }
    $cmd = Get-Command '7z' -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $cmd = Get-Command '7za' -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    throw ' 找不到 7z（请安装 7-Zip，或把它加进 PATH）'
}

function Format-Size([long]$Bytes) {
    if ($Bytes -ge 1GB) { return ('{0:N2} GB' -f ($Bytes / 1GB)) }
    if ($Bytes -ge 1MB) { return ('{0:N1} MB' -f ($Bytes / 1MB)) }
    return ('{0:N0} KB' -f ($Bytes / 1KB))
}

function ConvertTo-Bytes([string]$Value) {
    if (-not $Value) { return [long]0 }
    if ($Value -match '^\s*(\d+(?:\.\d+)?)\s*(KB|MB|GB|B)?\s*$') {
        $n = [double]$Matches[1]
        $unit = $Matches[2]
        switch ($unit) {
            'GB' { return [long]($n * 1GB) }
            'MB' { return [long]($n * 1MB) }
            'KB' { return [long]($n * 1KB) }
            default { return [long]$n }
        }
    }
    throw "无法解析体积：$Value（示例：1900MB / 1.5GB）"
}

function Get-FileSha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Copy-Tree([string]$Source, [string]$Dest, [string[]]$SkipDirs, [string[]]$SkipFiles) {
    $files = 0
    $bytes = [long]0
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
    $src = (Get-Item -LiteralPath $Source).FullName
    Get-ChildItem -LiteralPath $Source -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = $_.FullName.Substring($src.Length).TrimStart('\')
        $relDir = Split-Path -Parent $rel
        $skip = $false
        foreach ($d in $SkipDirs) {
            if ($rel -like "$d\*" -or $rel -eq $d -or $relDir -like "$d" -or $rel -like "*\$d\*") { $skip = $true; break }
        }
        if (-not $skip) {
            foreach ($f in $SkipFiles) {
                if ($_.Name -like $f) { $skip = $true; break }
            }
        }
        if ($skip) { return }
        $target = Join-Path $Dest $rel
        $parent = Split-Path -Parent $target
        if (-not (Test-Path -LiteralPath $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
        Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        $script:copiedFiles++
        $script:copiedBytes += $_.Length
    }
    return $script:copiedFiles
}

function Remove-TreeFast([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return }
    try {
        Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction Stop
    } catch {
        & cmd /c "rd /s /q `"$Path`"" 2>$null
    }
}

# =========================================================== 主流程 ====
if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }
if (-not $Version) {
    $cfgText = Get-Content -LiteralPath (Join-Path $Root 'config.yaml') -Raw -Encoding UTF8
    if ($cfgText -match '(?m)^version:\s*([0-9]+\.[0-9]+\.[0-9]+)') { $Version = $Matches[1] }
}
if (-not $Version) { throw '无法解析版本号：请显式传 -Version' }
if (-not $OutDir) { $OutDir = Join-Path $Root 'dist\desktop-release' }
if (-not $StagingDir) { $StagingDir = Join-Path $Root 'dist\desktop-staging' }

$maxBytes = ConvertTo-Bytes $MaxPartBytes
if ($maxBytes -le 0) { $maxBytes = 1900MB }
if ($maxBytes -gt 1900MB) { $maxBytes = 1900MB }
$maxMb = [int][math]::Floor($maxBytes / 1MB)
if ($maxMb -lt 1) { throw "分卷上限过小：$MaxPartBytes" }

$sevenZip = Find-SevenZip
New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
New-Item -ItemType Directory -Path $StagingDir -Force | Out-Null

Write-Host ''
Write-Host '==============================================' -ForegroundColor Cyan
Write-Host " Image MultiModel 桌面瘦包构建 v$Version" -ForegroundColor Cyan
Write-Host " 模式：$Mode · 分卷上限：$(Format-Size $maxBytes)" -ForegroundColor Cyan
Write-Host " 7z：$sevenZip" -ForegroundColor Cyan
Write-Host '==============================================' -ForegroundColor Cyan

$buildSlim = ($Mode -eq 'slim' -or $Mode -eq 'all')
$buildRuntime = ($Mode -eq 'runtime' -or $Mode -eq 'all')
$upload = New-Object System.Collections.ArrayList
$volumeObjs = @()
$runtimeVolObjs = @()
$catalogPath = Join-Path $OutDir $CatalogFileName

# ------------------------------------------------------ 引导解释器 ----
if ($buildSlim) {
    Write-Step '引导解释器（WinPython，仅 Web 依赖、无 torch）'
    if (-not $RuntimeDir) {
        if (-not (Test-Path -LiteralPath $WinPythonUrl)) {
            $dl = Join-Path $StagingDir 'WinPython.exe'
            Write-Host "  下载：$WinPythonUrl"
            Invoke-WebRequest -Uri $WinPythonUrl -OutFile $dl -UseBasicParsing -TimeoutSec 1800
            $WinPythonUrl = $dl
        }
        $extract = Join-Path $StagingDir '_wp'
        Remove-TreeFast $extract
        New-Item -ItemType Directory -Path $extract -Force | Out-Null
        Write-Host '  解压 WinPython ...'
        & $sevenZip x $WinPythonUrl "-o$extract" -y -bso0 -bsp0 | Out-Null
        $pyRoot = Get-ChildItem -LiteralPath $extract -Directory -Filter 'python-*' |
            Sort-Object Name -Descending | Select-Object -First 1
        if (-not $pyRoot) { throw "WinPython 解压后未找到 python-* 目录：$extract" }
        $RuntimeDir = $pyRoot.FullName
    }
    if (-not (Test-Path -LiteralPath (Join-Path $RuntimeDir 'python.exe'))) {
        throw "解释器目录缺少 python.exe：$RuntimeDir"
    }
    Write-Host "  解释器：$(Join-Path $RuntimeDir 'python.exe')"

    if (-not $SkipDeps) {
        # 只装非 torch 依赖：引导解释器的职责是把「下载管理」页跑起来。
        # 过滤掉 torch 家族与依赖 torch 的包（clip-anytorch / controlnet-aux / accelerate），
        # 否则 pip 会顺手把 CPU 版 torch 装回来，判定与体积双输。
        $reqSrc = Join-Path $Root 'requirements.txt'
        $reqNoTorch = Join-Path $StagingDir 'requirements-notorch.txt'
        $skipNames = @('torch', 'torchvision', 'torchaudio', 'clip-anytorch', 'controlnet-aux', 'accelerate')
        $lines = @()
        foreach ($line in [System.IO.File]::ReadAllLines($reqSrc)) {
            $s = $line.Trim()
            if (-not $s -or $s.StartsWith('#')) { continue }
            $name = ($s -split '[<>=!\[; ]')[0].Trim().ToLowerInvariant()
            if ($skipNames -contains $name) { continue }
            $lines += $s
        }
        $enc = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllLines($reqNoTorch, [string[]]$lines, $enc)
        Write-Host "  安装非 torch 依赖（$($lines.Count) 条）..."
        $prevCfg = $env:PIP_CONFIG_FILE
        $env:PIP_CONFIG_FILE = 'NUL'
        try {
            & (Join-Path $RuntimeDir 'python.exe') -m pip install -r $reqNoTorch --no-warn-script-location -q
        } finally {
            $env:PIP_CONFIG_FILE = $prevCfg
        }
        if ($LASTEXITCODE -ne 0) { throw "  非 torch 依赖安装失败（退出码 $LASTEXITCODE）" }
    } else {
        Write-Host '  跳过依赖安装（-SkipDeps）'
    }

    # 自检：必须有 fastapi（下载管理页要靠它），且必须没有 torch（那是环境包的事）
    $pyExe = Join-Path $RuntimeDir 'python.exe'
    $hasFastapi = (& $pyExe -c "import importlib.util as u;print('1' if u.find_spec('fastapi') else '0')") -join ''
    $hasTorch = (& $pyExe -c "import importlib.util as u;print('1' if u.find_spec('torch') else '0')") -join ''
    Write-Host "  自检：fastapi=$hasFastapi torch=$hasTorch"
    if ($hasFastapi.Trim() -ne '1') { throw '  引导解释器缺少 fastapi，无法运行下载管理页' }
    if ($hasTorch.Trim() -eq '1') { Write-Host '  引导解释器自带 torch，打包时将剔除' }
}

# -------------------------------------------------------- 数据卷载荷 ----
if ($buildSlim) {
    Write-Step '组装载荷（app\ + bootstrap\）'
    $payload = Join-Path $StagingDir 'data-payload'
    Remove-TreeFast $payload
    $appOut = Join-Path $payload $PayloadAppName
    New-Item -ItemType Directory -Path $appOut -Force | Out-Null

    $script:copiedFiles = 0
    $script:copiedBytes = [long]0
    foreach ($dir in $CodeDirs.Keys) {
        $src = Join-Path $Root $dir
        if (-not (Test-Path -LiteralPath $src)) { throw "缺少应用目录：$src" }
        $dest = Join-Path $appOut $CodeDirs[$dir]
        Copy-Tree -Source $src -Dest $dest -SkipDirs $ExcludeDirs -SkipFiles $ExcludeFiles | Out-Null
        Write-Host "  · $dir -> $($CodeDirs[$dir])"
    }
    foreach ($f in $CodeFiles) {
        $src = Join-Path $Root $f
        if (-not (Test-Path -LiteralPath $src)) { Write-Warning "  跳过不存在的文件：$f"; continue }
        Copy-Item -LiteralPath $src -Destination (Join-Path $appOut $f) -Force
        $script:copiedFiles++
        $script:copiedBytes += (Get-Item -LiteralPath $src).Length
    }

    # 下载清单：有 -Mode runtime 产出的清单就带上（含真实分卷与哈希），否则用仓库基线
    $seedCatalog = Join-Path $Root 'app\downloads_catalog.json'
    if (Test-Path -LiteralPath $catalogPath) {
        Copy-Item -LiteralPath $catalogPath -Destination (Join-Path $appOut $CatalogFileName) -Force
        Write-Host "  清单：来自本次 runtime 构建（$catalogPath）"
    } elseif (Test-Path -LiteralPath $seedCatalog) {
        Copy-Item -LiteralPath $seedCatalog -Destination (Join-Path $appOut $CatalogFileName) -Force
        Write-Host "  清单：仓库基线（$seedCatalog，分卷可能为空）"
    } else {
        Write-Warning "  未找到 downloads_catalog.json，下载管理页将提示清单缺失"
    }

    # 运行态空目录骨架（首次安装就要存在，避免运行期首次写盘失败）
    foreach ($d in @('data\cache', 'data\uploads', 'outputs', 'logs')) {
        New-Item -ItemType Directory -Path (Join-Path $appOut $d) -Force | Out-Null
    }

    # 引导解释器 → <payload>\bootstrap\
    $bootOut = Join-Path $payload $BootstrapDirName
    Write-Host '  复制解释器（数万文件，稍候）...'
    $rc = Start-Process -FilePath 'robocopy' -ArgumentList @(
        $RuntimeDir, $bootOut, '/E', '/NFL', '/NDL', '/NJH', '/NJS', '/R:1', '/W:1',
        '/XD', 'notebooks', 'Lib\site-packages\torch', 'Lib\site-packages\torchvision',
        'Lib\site-packages\torchaudio', 'Lib\site-packages\torchgen'
    ) -Wait -PassThru -NoNewWindow
    if ($rc.ExitCode -ge 8) { throw "  robocopy 复制解释器失败（退出码 $($rc.ExitCode)）" }

    # 剔除 WinPython 自带的 torch（实测 CPU 版、552 MB、CUDA 不可用）：
    #   ① 瘦包本就不该带 torch；② 留着会让「是否已装环境」的判定失真。
    $sitePackages = Join-Path $bootOut 'Lib\site-packages'
    foreach ($pkg in @('torch', 'torchvision', 'torchaudio', 'torchgen')) {
        $pkgDir = Join-Path $sitePackages $pkg
        if (Test-Path -LiteralPath $pkgDir) {
            Remove-TreeFast $pkgDir
            Write-Host "    剔除自带 $pkg"
        }
        Get-ChildItem -LiteralPath $sitePackages -Directory -Filter "$pkg-*.dist-info" -ErrorAction SilentlyContinue |
            ForEach-Object { Remove-TreeFast $_.FullName; Write-Host "    剔除 $($_.Name)" }
        Get-ChildItem -LiteralPath $sitePackages -Directory -Filter "$pkg.*.dist-info" -ErrorAction SilentlyContinue |
            ForEach-Object { Remove-TreeFast $_.FullName }
    }
    # 引导解释器不该带 RUNTIME.json（那是「已装环境」的判据）
    $staleMeta = Join-Path $bootOut 'RUNTIME.json'
    if (Test-Path -LiteralPath $staleMeta) { Remove-Item -LiteralPath $staleMeta -Force }

    # 载荷结构断言（与壳/后端的路径约定一一对应）
    $must = @(
        (Join-Path $appOut 'integrated_app\app_server.py'),
        (Join-Path $appOut 'config.yaml'),
        (Join-Path $bootOut 'python.exe')
    )
    foreach ($m in $must) {
        if (-not (Test-Path -LiteralPath $m)) { throw "载荷不完整，缺少 $m" }
    }
    if (Test-Path -LiteralPath (Join-Path $bootOut 'Lib\site-packages\torch')) {
        throw '载荷仍包含 torch，瘦包不允许带 torch'
    }
    if (Test-Path -LiteralPath (Join-Path $bootOut 'RUNTIME.json')) {
        throw '载荷包含 RUNTIME.json，会让壳误判为已装环境'
    }

    $bytes = (Get-ChildItem -LiteralPath $payload -Recurse -File -Force | Measure-Object -Property Length -Sum).Sum
    Write-Host ("  载荷：{0} 文件 / {1}（未压缩）" -f $script:copiedFiles, (Format-Size $bytes))

    Write-Step '数据卷（7z 分卷）'
    $arcBase = Join-Path $StagingDir $DataArchiveName
    Remove-Item -LiteralPath $arcBase -Force -ErrorAction SilentlyContinue
    Push-Location $payload
    try {
        & $sevenZip a -t7z "-mx=$Level" "-v${maxMb}m" $arcBase $PayloadAppName $BootstrapDirName | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "7z 打包失败（退出码 $LASTEXITCODE）" }
    } finally {
        Pop-Location
    }

    $vols = @(Get-ChildItem -LiteralPath $StagingDir -File -Filter "$DataArchiveName*" | Sort-Object Name)
    $index = 0
    foreach ($v in $vols) {
        $index++
        $target = Join-Path $OutDir $v.Name
        Move-Item -LiteralPath $v.FullName -Destination $target -Force
        $obj = [pscustomobject]@{ Index = $index; Name = $v.Name; Bytes = $v.Length; Sha256 = (Get-FileSha256 $target) }
        $volumeObjs += $obj
        [void]$upload.Add($target)
        Write-Host ("    卷 {0}/{1}：{2}  {3}" -f $index, $vols.Count, (Format-Size $v.Length), $v.Name)
    }
    if (-not $KeepArchive) {
        Remove-Item -LiteralPath $arcBase -Force -ErrorAction SilentlyContinue
    }
    if (-not $KeepStaging) { Remove-TreeFast $payload }
}

# ---------------------------------------------------------- 环境包 ----
if ($buildRuntime) {
    Write-Step "环境包（torch $TorchVersion + torchvision $TorchvisionVersion，$TorchIndexUrl）"
    $dlPython = if ($RuntimeDir -and (Test-Path -LiteralPath (Join-Path $RuntimeDir 'python.exe'))) {
        Join-Path $RuntimeDir 'python.exe'
    } else { 'python' }
    $pyVer = (& $dlPython -c "import sys;print(sys.version.split()[0])") -join ''
    Write-Host "  下载用解释器：$dlPython（Python $pyVer）"

    $wheels = Join-Path $StagingDir 'wheels'
    Remove-TreeFast $wheels
    New-Item -ItemType Directory -Path $wheels -Force | Out-Null
    $prevCfg = $env:PIP_CONFIG_FILE
    $env:PIP_CONFIG_FILE = 'NUL'
    try {
        & $dlPython -m pip download "torch==$TorchVersion" "torchvision==$TorchvisionVersion" `
            --index-url $TorchIndexUrl -d $wheels --no-warn-script-location
    } finally {
        $env:PIP_CONFIG_FILE = $prevCfg
    }
    if ($LASTEXITCODE -ne 0) { throw "下载 torch wheels 失败（退出码 $LASTEXITCODE）" }
    $whlCount = @(Get-ChildItem -LiteralPath $wheels -File -Filter '*.whl').Count
    if ($whlCount -eq 0) { throw "wheels 目录为空：$wheels" }
    Write-Host "  下载完成：$whlCount 个 wheel"

    $zipBase = Join-Path $StagingDir $RuntimeZipName
    Remove-Item -LiteralPath $zipBase -Force -ErrorAction SilentlyContinue
    Push-Location $wheels
    try {
        # Level 0：wheel 本身已压缩，再压收益极低但很慢
        & $sevenZip a -tzip -mx=0 "-v${maxMb}m" $zipBase '*' | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "打包环境包失败（退出码 $LASTEXITCODE）" }
    } finally {
        Pop-Location
    }

    $rtVols = @(Get-ChildItem -LiteralPath $StagingDir -File -Filter "$RuntimeZipName*" | Sort-Object Name)
    $index = 0
    $totalBytes = [long]0
    foreach ($v in $rtVols) {
        $index++
        $target = Join-Path $OutDir $v.Name
        Move-Item -LiteralPath $v.FullName -Destination $target -Force
        $totalBytes += $v.Length
        $runtimeVolObjs += [pscustomobject]@{ Index = $index; Name = $v.Name; Bytes = $v.Length; Sha256 = (Get-FileSha256 $target) }
        [void]$upload.Add($target)
        Write-Host ("    卷 {0}/{1}：{2}  {3}" -f $index, $rtVols.Count, (Format-Size $v.Length), $v.Name)
    }
    if (-not $KeepArchive) { Remove-Item -LiteralPath $zipBase -Force -ErrorAction SilentlyContinue }
    if (-not $KeepStaging) { Remove-TreeFast $wheels }

    $cuda = 'cpu'
    if ($TorchIndexUrl -match '/whl/([^/]+)/?$') { $cuda = $Matches[1] }

    $catalog = [ordered]@{
        schema  = 1
        runtime = [ordered]@{
            version         = '1'
            tag             = $RuntimeDefaultTag
            base_url        = "$ReleaseBase/$RuntimeDefaultTag"
            python          = $pyVer
            torch           = "$TorchVersion+$cuda"
            cuda            = $cuda
            packages        = @("torch==$TorchVersion", "torchvision==$TorchvisionVersion")
            size_bytes      = [long]$totalBytes
            built_at        = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
            min_app_version = $Version
            volumes         = @(
                foreach ($v in $runtimeVolObjs) {
                    [ordered]@{ name = $v.Name; size = [long]$v.Bytes; sha256 = $v.Sha256 }
                }
            )
        }
        models  = @()
    }
    $json = $catalog | ConvertTo-Json -Depth 8
    [System.IO.File]::WriteAllText($catalogPath, $json, (New-Object System.Text.UTF8Encoding($false)))
    [void]$upload.Add($catalogPath)
    Write-Host "  清单：$catalogPath"
}

# ------------------------------------------------------ SHA256SUMS ----
$sumFile = Join-Path $OutDir 'SHA256SUMS.txt'
$sumLines = @()
foreach ($p in $upload) {
    if (Test-Path -LiteralPath $p -PathType Leaf) {
        $sumLines += ("{0}  {1}" -f (Get-FileSha256 $p), (Split-Path -Leaf $p))
    }
}
if ($sumLines.Count -gt 0) {
    [System.IO.File]::WriteAllLines($sumFile, [string[]]$sumLines, (New-Object System.Text.UTF8Encoding($false)))
    [void]$upload.Add($sumFile)
    Write-Host ''
    Write-Host "[清单] SHA256SUMS.txt（$($sumLines.Count) 项）"
}

# --------------------------------------------------------- manifest ----
$manifest = [ordered]@{
    schema       = 1
    product      = 'Image-MultiModel-Desktop'
    app_version  = $Version
    mode         = $Mode
    arch         = 'win-x64'
    created_utc  = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
    max_part_mb  = $maxMb
    installer    = "ImageMultiModel-Setup-v$Version.exe"
    data_archive = $DataArchiveName
    shell_exe    = $ProductExe
    bootstrap    = "$BootstrapDirName\python.exe"
    payload_layout = @("$PayloadAppName\", "$BootstrapDirName\")
    unpack_note  = '数据分卷必须与安装器同目录；安装器用内嵌 7za 解 ImageMultiModel-Data.7z.001 到安装目录'
    data_volumes = @(
        foreach ($v in $volumeObjs) {
            [ordered]@{ index = $v.Index; file = $v.Name; bytes = [long]$v.Bytes; sha256 = $v.Sha256 }
        }
    )
    runtime_volumes = @(
        foreach ($v in $runtimeVolObjs) {
            [ordered]@{ index = $v.Index; file = $v.Name; bytes = [long]$v.Bytes; sha256 = $v.Sha256 }
        }
    )
}
$manifestPath = Join-Path $OutDir 'manifest.json'
[System.IO.File]::WriteAllText($manifestPath, ($manifest | ConvertTo-Json -Depth 8), (New-Object System.Text.UTF8Encoding($false)))
[void]$upload.Add($manifestPath)

[System.IO.File]::WriteAllLines(
    (Join-Path $OutDir 'upload-list.txt'),
    [string[]]$upload,
    (New-Object System.Text.UTF8Encoding($false))
)

$total = [long]0
foreach ($p in $upload) { if (Test-Path -LiteralPath $p -PathType Leaf) { $total += (Get-Item -LiteralPath $p).Length } }
Write-Host ''
Write-Host "[完成] 产物目录：$OutDir" -ForegroundColor Green
Write-Host ("[完成] 共 {0} 个待上传文件，合计 {1}" -f $upload.Count, (Format-Size $total)) -ForegroundColor Green
Write-Host "[下一步] 编译安装器：cd desktop\installer; makensis /DAPP_VERSION=$Version setup.nsi" -ForegroundColor Green
