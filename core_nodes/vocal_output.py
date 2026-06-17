# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: NATIVE SYSTEM SPEECH SYNTHESIS ENGINE
# COMPLIANCE: ZERO EM-DASHES; MULTI-THREADED AUDIO PLAYBACK
# ==============================================================================

import os
import sys
import subprocess
import threading

# Ensure stdout and stderr use UTF-8 encoding on Windows consoles to prevent UnicodeEncodeError
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


class VocalResponse:
    """Utilizes system Speech Synthesizer to provide local verbal audio response feedback."""

    def __init__(self):
        self.lock = threading.Lock()

    def speak(self, text: str) -> bool:
        """Synthesizes input text and plays it back immediately via the default audio output device.

        This method dispatches the SAPI execution call inside a separate background thread
        to prevent blocking main Swarm execution pipelines.
        """
        if not text:
            return False

        def _execute_native_tts():
            with self.lock:
                try:
                    # Escape single quotes for PowerShell string validation safety
                    escaped_text = text.replace("'", "''")
                    
                    # Command invoking the native SAPI SpeechSynthesizer
                    cmd = (
                        f"Add-Type -AssemblyName System.Speech; "
                        f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                        f"$synth.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Neutral); "
                        f"$synth.Speak('{escaped_text}')"
                    )
                    
                    # Execute powershell process silently in background
                    subprocess.run(
                        ["powershell", "-Command", cmd],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                    )
                except Exception as err:
                    sys.stderr.write(f"Vocal Output: Text-to-Speech execution failure: {str(err)}\n")

        # Spawn background thread for audio playback concurrency
        thread = threading.Thread(target=_execute_native_tts, daemon=True)
        thread.start()
        return True


if __name__ == "__main__":
    print("==========================================================")
    print(" INITIALIZING GOINGS OS SYSTEM VOCAL OUTPUT NODE           ")
    print("==========================================================")
    
    response = VocalResponse()
    print(" -> Transmitting test vocal message...")
    response.speak("Goings OS vocal output system initialized: status is healthy.")
    
    # Wait for background playback to complete
    import time
    time.sleep(4.0)
    print("==========================================================")
