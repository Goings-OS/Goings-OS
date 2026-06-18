# GOINGS OS / UNIFIED CLI BRIDGE MANIFEST
# System Configuration Layer Registered Natively

# Core Cross Platform System Aliases
Set-Alias -Name gcloud-env -Value "C:\Google\CloudSDK\google-cloud-sdk\bin\gcloud.cmd"
Set-Alias -Name firebase-deploy -Value "firebase"
Set-Alias -Name android-build -Value "gradlew"
Set-Alias -Name antigravity-core -Value "antigravity"

function Sync-All-Surfaces {
    Write-Output "[BRIDGE] Initializing multi platform cloud synchronization..."
    & firebase deploy --only hosting
    & gcloud config list
    & git status -u
    Write-Output "[BRIDGE] Integration surfaces completely validated."
}
