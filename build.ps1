<#
.SYNOPSIS
    Windows PowerShell 版本的專案管理腳本，對應原本 Makefile 的各個 target。

.USAGE
    .\build.ps1 <task>

    範例:
        .\build.ps1 init
        .\build.ps1 run
        .\build.ps1 python-lint
        .\build.ps1 help

.NOTES
    - 需要先在 PowerShell 中允許執行腳本:
        Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
    - 假設已安裝 Python 3.13、Node.js/npm、git、pre-commit、cloc、pylint 等工具，
      且皆已加入系統 PATH。
#>

param(
    [Parameter(Position = 0)]
    [string]$Task = "help"
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------
# 基本變數設定 (對應 Makefile 開頭)
# ---------------------------------------------------------
$Python = "python.exe"
$VenvActivate = ".\venv\Scripts\Activate.ps1"

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
    }
}

# 讀取 .env 並設成環境變數 (對應 Makefile 的 include .env / export)
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#=]+?)\s*=\s*(.*)\s*$') {
            $name = $matches[1]
            $value = $matches[2]
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

function Print-Banner {
    param([string]$Message)
    Write-Host "==============================================================================="
    Write-Host $Message
    Write-Host "==============================================================================="
}

# ---------------------------------------------------------
# 一般 targets
# ---------------------------------------------------------
function Task-Init {
    Print-Banner "Initializing local development environment. This will verify and set up your`nPython virtual environment, install all 3rd-party package requirements.`nThis may take a few minutes..."
    Task-PythonInit
    Print-Banner "Initialization complete!"
}

function Task-Activate {
    if (Test-Path $VenvActivate) {
        & $VenvActivate
    } else {
        Write-Warning "找不到 $VenvActivate，請先執行 .\build.ps1 python-init"
    }
}

function Task-Run {
    Print-Banner "Running solution ..."
    Task-PythonFetchData
    Task-PythonBuildDataset
}

function Task-TearDown {
    Print-Banner "Tearing down solution ..."
    Task-PythonClean
}

function Task-PreCommitInit {
    Print-Banner "Installing and configuring pre-commit ..."
    pre-commit install
    pre-commit autoupdate
}

function Task-PreCommitRun {
    Print-Banner "Running pre-commit hooks on all files ..."
    pre-commit run --all-files
}

function Task-Release {
    Print-Banner "Forcing a new semantic release on GitHub by creating an empty commit and pushing to the repository ..."
    git commit -m "fix: force a new release" --allow-empty
    git push
}

function Task-Analyze {
    Print-Banner "Generating code analysis report using cloc ..."
    cloc . --exclude-ext=svg,zip --fullpath --not-match-d=smarter/smarter/static/assets/ --vcs=git
}

# ---------------------------------------------------------
# Python targets
# ---------------------------------------------------------
function Task-CheckPython {
    Write-Host ""
    Print-Banner "Verifying that Python $Python is installed ..."
    Write-Host ""
    $found = Get-Command $Python -ErrorAction SilentlyContinue
    if (-not $found) {
        Write-Error "This project requires $Python but it's not installed. Aborting."
        python --version
        exit 1
    }
}

function Task-PythonInit {
    Print-Banner "Initializing Python virtual environment and installing dependencies. This may take a few minutes..."

    if (Test-Path "venv") {
        Remove-Item -Recurse -Force "venv"
    }
    New-Item -ItemType Directory -Force -Path ".pypi_cache" | Out-Null

    Task-CheckPython
    Task-PythonClean

    npm install

    & $Python -m venv venv
    & $VenvActivate

    $env:PIP_CACHE_DIR = ".pypi_cache"
    & $Python -m pip install pip==25.3 setuptools wheel pip-tools
    & $Python -m pip install -r requirements\local.txt

    & $Python -m ipykernel install --user --name py311 --display-name "Python 3.13"
}

function Task-PythonLint {
    Write-Host ""
    Print-Banner "Running Python linting using pre-commit ..."
    Write-Host ""
    Task-CheckPython
    Task-PreCommitRun
    pylint netflix
}

function Task-PythonClean {
    Write-Host ""
    Print-Banner "Cleaning Python virtual environment and __pycache__ directories ..."
    Write-Host ""
    if (Test-Path "venv") {
        Remove-Item -Recurse -Force "venv"
    }
    Get-ChildItem -Path ".\netflix" -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
}

function Task-PythonRequirements {
    Print-Banner "Compiling and updating Python dependency files using pip-compile ..."
    pip install pip==25.3 setuptools wheel pip-tools
    pip-compile requirements\in\base.in -o requirements\base.txt
    pip-compile requirements\in\local.in -o requirements\local.txt
}

function Task-PythonFetchData {
    Print-Banner "Fetching data from external APIs and saving to local files ..."
    & $VenvActivate
    python -m netflix.fetch
}

function Task-PythonBuildDataset {
    Print-Banner "Building composite Netflix dataset from fetched data ..."
    & $VenvActivate
    python -m netflix.build
}

function Task-PythonBuildStories {
    Print-Banner "Building  ..."
    & $VenvActivate
    python -m netflix.build.story_codes
}

# ---------------------------------------------------------
# HELP
# ---------------------------------------------------------
function Task-Help {
    Write-Host '===================================================================='
    Write-Host 'init                   - Initialize local and Docker environments'
    Write-Host 'activate               - Activate Python virtual environment'
    Write-Host 'run                    - Run web application from Docker'
    Write-Host 'tear-down              - Destroy all Docker build and local artifacts'
    Write-Host 'pre-commit-init        - Install and configure pre-commit hooks'
    Write-Host 'pre-commit-run         - Run pre-commit hooks on all files'
    Write-Host 'release                - Force a new semantic release on GitHub by creating an empty commit and pushing to the repository'
    Write-Host 'analyze                - Generate code analysis report using cloc'
    Write-Host '<************************** Python **************************>'
    Write-Host 'check-python           - Verify Python 3.13 is installed'
    Write-Host 'python-init            - Create a Python virtual environment and install dependencies'
    Write-Host 'python-lint            - Run Python linting using pre-commit and pylint'
    Write-Host 'python-clean           - Destroy the Python virtual environment and remove __pycache__ directories'
    Write-Host 'python-requirements    - Compile and update Python dependency files'
    Write-Host 'python-fetch-data      - Fetch data from external APIs and save to local files'
    Write-Host 'python-build-dataset   - Build composite Netflix dataset from fetched data'
    Write-Host 'python-build-stories   - Build story codes'
    Write-Host '===================================================================='
}

# ---------------------------------------------------------
# 任務分派 (對應 make 的 target 呼叫方式)
# ---------------------------------------------------------
switch ($Task.ToLower()) {
    "init"                 { Task-Init }
    "activate"              { Task-Activate }
    "run"                   { Task-Run }
    "tear-down"             { Task-TearDown }
    "pre-commit-init"       { Task-PreCommitInit }
    "pre-commit-run"        { Task-PreCommitRun }
    "release"               { Task-Release }
    "analyze"                { Task-Analyze }
    "check-python"           { Task-CheckPython }
    "python-init"            { Task-PythonInit }
    "python-lint"            { Task-PythonLint }
    "python-clean"           { Task-PythonClean }
    "python-requirements"    { Task-PythonRequirements }
    "python-fetch-data"      { Task-PythonFetchData }
    "python-build-dataset"   { Task-PythonBuildDataset }
    "python-build-stories"   { Task-PythonBuildStories }
    default                  { Task-Help }
}