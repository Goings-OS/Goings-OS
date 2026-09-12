# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: BACK OFFICE AS A SERVICE INITIALIZER (deploy_baas_office.ps1)
# COMPLIANCE: ZERO EM-DASHES; PRIVATE GOVERNOR FORMULATIONS
# ==============================================================================

# Verify Administrative Privileges
$Identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$Principal = New-Object Security.Principal.WindowsPrincipal($Identity)
$IsAdmin = $Principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin) {
    Write-Error "Deployer must be run from an elevated Administrator session; exiting."
    exit 1
}

# Define Target Directories
$BaaSVolume = "C:\Goings-BaaS-Core"
$ConfigDir = "$BaaSVolume\configurations"
$DaemonDir = "$BaaSVolume\runtime_daemons"
$KBDir = "$BaaSVolume\knowledge_base"

Write-Output "[BAAS_DEPLOYER] Initializing client installation sequence..."

# Create directory tree structures if missing
$TargetDirs = @($ConfigDir, $DaemonDir, $KBDir)
foreach ($Dir in $TargetDirs) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Force -Path $Dir | Out-Null
        Write-Output "[BAAS_DEPLOYER] Created directory: $Dir"
    } else {
        Write-Output "[BAAS_DEPLOYER] Directory already exists: $Dir"
    }
}

# Deploy default environment configuration layout
$ConfigPath = "$ConfigDir\env_config.json"
$ConfigPayload = @{
    "client_id" = "CLI-CLIENT-DEFAULT"
    "deployment_mode" = "PRIVATE_GOVERNOR"
    "ingress_gateway_port" = 5000
    "insulation_reserve_ratio" = 0.20
    "owners_draw_ratio" = 0.50
    "created_at" = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
} | ConvertTo-Json

Write-Output "[BAAS_DEPLOYER] Writing default config schema to: $ConfigPath"
$ConfigPayload | Out-File -FilePath $ConfigPath -Encoding utf8 -Force

# Execute pip commands to install core system requirements
Write-Output "[BAAS_DEPLOYER] Resolving and downloading core dependencies..."
$PythonCommand = "python"
if (Get-Command python -ErrorAction SilentlyContinue) {
    # Install dependencies inside the host Python context
    & $PythonCommand -m pip install fastapi waitress curl_cffi a2wsgi beautifulsoup4 --upgrade
} else {
    Write-Error "[BAAS_DEPLOYER] Python environment not detected in PATH; manual package install needed."
}

Write-Output "[BAAS_DEPLOYER] [SUCCESS] Installation sequence finished."
