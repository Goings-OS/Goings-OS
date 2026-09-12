import os
import re

target_path = r"core_nodes\node_13_developer\companion_app\implementation_plan.md"
# Fallback check to find the file if located in the default brain cache folder
if not os.path.exists(target_path):
    target_path = r"C:\Google\CloudSDK\Goings-OS\notebook_sources\implementation_plan.md"

if os.path.exists(target_path):
    print(f"[REFACTOR] Padding structural layouts for: {target_path}")
    with open(target_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    formatted_lines = []
    for line in lines:
        stripped = line.strip()
        # Enforce clean vertical boundaries for headings and bullet points (MD022 / MD032)
        if stripped.startswith("#") or stripped.startswith("* ") or stripped.startswith("- "):
            formatted_lines.append("\n" + line + "\n")
        else:
            formatted_lines.append(line)
            
    clean_text = re.sub(r"\n{3,}", "\n\n", "".join(formatted_lines))
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(clean_text.strip() + "\n")
    print("[SUCCESS] Markdown compliance layout completely stabilized.")
else:
    print("[NOTE] File path routing outside primary directory block. Ready for workspace refresh.")
