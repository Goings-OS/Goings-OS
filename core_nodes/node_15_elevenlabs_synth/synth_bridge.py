import os
import sys
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Ingest local environmental parameters safely
load_dotenv()

class ElevenLabsProductionBridge:
    def __init__(self):
        # Bind the enterprise engine tokens strictly from local environment variables
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        
        if not self.api_key:
            print("[CRITICAL ERROR] ElevenLabs API Key missing from local context.")
            sys.exit(1)
            
        # Initialize the official secure enterprise client pipeline
        self.client = ElevenLabs(api_key=self.api_key)

    def execute_synthesis(self, input_text, target_output_path="output.mp3"):
        """Compiles text strings to high resolution speech using the ultra low latency model."""
        print(f"[SYNTH ACTIVE] Materializing voice output tracking for text: {input_text[:30]}...")
        
        try:
            # Leveraging the optimized eleven_flash_v2_5 engine architecture
            audio_generator = self.client.generate(
                text=input_text,
                voice=self.voice_id if self.voice_id else "Rachel",
                model="eleven_flash_v2_5"
            )
            
            # Write stream chunks cleanly directly to the target node destination
            with open(target_output_path, "wb") as file_stream:
                for audio_chunk in audio_generator:
                    file_stream.write(audio_chunk)
                    
            print(f"[SUCCESS] Audio payload safely written to disk: {target_output_path}")
            return True
            
        except Exception as execution_fault:
            print(f"[SYSTEM INTEGRATION FAULT] Audio engine failure encountered: {str(execution_fault)}")
            return False

if __name__ == "__main__":
    # Test initialization routine
    bridge_instance = ElevenLabsProductionBridge()
    print("[STATUS] ElevenLabs enterprise synthesis client node initialized successfully.")
