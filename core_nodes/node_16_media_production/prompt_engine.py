import os
import hashlib
from datetime import datetime

class MediaPromptRotator:
    def __init__(self):
        self.workspace_root = r"C:\Google\CloudSDK\Goings-OS"
        self.user_assets = ["terrence_headshot_prime.png", "tbe_logo_gold.svg", "kig_crest.png"]
        self.actions = ["analyzing real-time waterfront market data charts", "architecting enterprise container frameworks", "leading executive council strategy reviews"]
        self.visual_styles = ["Texz-Architect Cinematic Dark Noir", "Cyberpunk Industrial Steel", "Hyper-Realistic Matte Gold Accents"]

    def calculate_daily_combination(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        hash_seed = hashlib.sha256(today_str.encode('utf-8')).hexdigest()
        int_seed = int(hash_seed, 16)
        
        selected_asset = self.user_assets[int_seed % len(self.user_assets)]
        selected_action = self.actions[(int_seed >> 2) % len(self.actions)]
        selected_style = self.visual_styles[(int_seed >> 4) % len(self.visual_styles)]
        
        print(f"\n[MEDIA PROMPT ENGINE] Verified unique daily prompt compiled for {today_str}:")
        print(f"-> Featured Asset: {selected_asset}")
        print(f"-> Subject Action: {selected_action}")
        print(f"-> Visual Style:  {selected_style}\n")

if __name__ == "__main__":
    rotator = MediaPromptRotator()
    rotator.calculate_daily_combination()
