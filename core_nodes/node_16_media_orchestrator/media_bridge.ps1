# GOINGS OS // MEDIA ORCHESTRATION BRIDGE
# Google Vids & LiveKit Unified Streaming Interface

# Connection Parameters
$env:GOOGLE_VIDS_API_KEY = "PLACEHOLDER_KEY"
$env:LIVEKIT_WS_URL = "wss://livekit.goingsos.com"

function Start-Media-Pipeline {
    Write-Output "[MEDIA] Initializing Google Vids Avatar Generation..."
    # Call to node_16 orchestrator script
    python core_nodes/node_16_media_orchestrator/orchestrator.py
}
