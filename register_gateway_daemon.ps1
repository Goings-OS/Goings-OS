# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: WEBHOOK INGRESS DAEMON REGISTRATION (register_gateway_daemon.ps1)
# COMPLIANCE: ZERO EM-DASHES; PRIVATE GOVERNOR FORMULATIONS
# ==============================================================================

# Define workspace directories
$WorkspaceRoot = "C:\Google\CloudSDK\Goings-OS"
$PythonPath = "$WorkspaceRoot\.venv\Scripts\python.exe"
$ScriptPath = "$WorkspaceRoot\ingress_gateway.py"

# Verify path integrity
if (-not (Test-Path $PythonPath)) {
    Write-Error "Private Python interpreter not found at $PythonPath; resolve paths."
    exit 1
}

if (-not (Test-Path $ScriptPath)) {
    Write-Error "Private Ingress Gateway script not found at $ScriptPath; resolve paths."
    exit 1
}

# Task settings definitions
$TaskName = "GoingsOS_Private_Ingress_Gateway"
$Description = "Executes the Private Ingress Gateway 24/7 as a background daemon service."

Write-Output "[$TaskName] Registering Private daemon service..."

# Define scheduled task action
# Runs the python script within the virtual environment inside the correct working directory
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptPath -WorkingDirectory $WorkspaceRoot

# Define scheduled task triggers: starts automatically on system startup
$Trigger = New-ScheduledTaskTrigger -AtStartup

# Define execution settings: ensure service doesn't shut down on battery power
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Define security credentials: runs as SYSTEM with highest privilege level
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register task to system
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description $Description -Force

# Confirm successful task registry
$RegisteredTask = Get-ScheduledTask -TaskName $TaskName
if ($RegisteredTask) {
    Write-Output "[$TaskName] [SUCCESS] Private daemon successfully registered."
    Write-Output "[$TaskName] Status: $($RegisteredTask.State)"
} else {
    Write-Error "[$TaskName] [FAILURE] Failed to register Private daemon task scheduler."
}
