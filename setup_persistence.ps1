# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# SCRIPT: BACKGROUND PERSISTENCE SETUP (setup_persistence.ps1)
# COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; RESILIENT DUAL-MODE PERSISTENCE
# ==============================================================================

param (
    [string]$TaskName = "GoingsOS_IngressGateway",
    [string]$WorkingDir = "C:\Google\CloudSDK\Goings-OS",
    [string]$PythonwPath = "C:\Google\CloudSDK\Goings-OS\venv\Scripts\pythonw.exe"
)

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host " GOINGS OS v4.2 // PERSISTENCE SERVICE REGISTRATION           " -ForegroundColor Cyan
Write-Host " COMPLIANCE: ZERO EM-DASHES; ZERO DOUBLE-HYPHENS; HEADLESS    " -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan

# 1. Resolve Pythonw executable
if (-not (Test-Path $PythonwPath)) {
    $systemPythonw = (Get-Command pythonw.exe -ErrorAction SilentlyContinue).Source
    if ($systemPythonw) {
        $PythonwPath = $systemPythonw
        Write-Host "[INFO] Using system pythonw: $PythonwPath" -ForegroundColor Yellow
    } else {
        Write-Error "[ERROR] pythonw.exe could not be located in venv or system PATH."
        exit 1
    }
} else {
    Write-Host "[INFO] Using virtual environment pythonw: $PythonwPath" -ForegroundColor Green
}

$ScriptPath = Join-Path $WorkingDir "ingress_gateway.py"
if (-not (Test-Path $ScriptPath)) {
    Write-Error "[ERROR] Target script $ScriptPath does not exist."
    exit 1
}

# 2. Attempt Mode A: Windows Scheduled Task (Requires Elevated Privileges)
$TaskRegistered = $false
try {
    Write-Host "[INFO] Attempting Windows Scheduled Task registration..." -ForegroundColor Cyan
    $Action = New-ScheduledTaskAction `
        -Execute $PythonwPath `
        -Argument "ingress_gateway.py" `
        -WorkingDirectory $WorkingDir

    $TriggerLogon = New-ScheduledTaskTrigger -AtLogOn
    $Settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit (New-TimeSpan -Days 0) `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 1) `
        -StartWhenAvailable

    $CurrentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $Principal = New-ScheduledTaskPrincipal -UserId $CurrentUser -LogonType Interactive -RunLevel Limited

    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    }

    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $TriggerLogon `
        -Settings $Settings `
        -Principal $Principal `
        -Description "Goings-OS v4.2 Private Ingress Gateway headless service listener on port 8080." `
        -ErrorAction Stop | Out-Null

    $TaskRegistered = $true
    Write-Host "[SUCCESS] Mode A: Scheduled Task $TaskName registered successfully!" -ForegroundColor Green
} catch {
    Write-Host "[NOTICE] Scheduled Task registration requires elevated Administrator privileges." -ForegroundColor Yellow
    Write-Host "[NOTICE] Falling back to Mode B: User Startup Autostart Shortcut (Zero-Admin Required)..." -ForegroundColor Yellow
}

# 3. Mode B: User Startup Directory Shortcut (100% Non-Admin Guaranteed Startup)
$StartupDir = [System.IO.Path]::Combine($env:APPDATA, "Microsoft\Windows\Start Menu\Programs\Startup")
$ShortcutPath = Join-Path $StartupDir "$TaskName.lnk"

try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $PythonwPath
    $Shortcut.Arguments = "ingress_gateway.py"
    $Shortcut.WorkingDirectory = $WorkingDir
    $Shortcut.Description = "Goings-OS v4.2 Private Ingress Gateway Headless Service"
    $Shortcut.WindowStyle = 7 # Minimized / Hidden window
    $Shortcut.Save()

    Write-Host "[SUCCESS] Mode B: User Startup Shortcut configured successfully!" -ForegroundColor Green
    Write-Host "Shortcut Path: $ShortcutPath" -ForegroundColor Green
    Write-Host "Executable: $PythonwPath" -ForegroundColor Green
    Write-Host "Target Script: ingress_gateway.py" -ForegroundColor Green
    Write-Host "Working Directory: $WorkingDir" -ForegroundColor Green
} catch {
    Write-Error "[ERROR] Failed to create Startup shortcut: $_"
    exit 1
}

# 4. Create standalone runner helper for manual or daemon restarts
$RunnerBat = Join-Path $WorkingDir "run_gateway_headless.vbs"
$VbsContent = "Set WshShell = CreateObject(""WScript.Shell"")`r`nWshShell.CurrentDirectory = ""$WorkingDir""`r`nWshShell.Run """"""$PythonwPath"""" ingress_gateway.py"", 0, False"
[System.IO.File]::WriteAllText($RunnerBat, $VbsContent, [System.Text.Encoding]::ASCII)
Write-Host "[INFO] Created headless VBS runner: $RunnerBat" -ForegroundColor Cyan

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host " GOINGS OS v4.2 PERSISTENCE ACTIVE: RUNS AUTOMATICALLY ON BOOT " -ForegroundColor Green
Write-Host "==============================================================" -ForegroundColor Cyan
