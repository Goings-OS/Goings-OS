import os
import re

def repair_markdown_syntax(file_path):
    if not os.path.exists(file_path):
        return False
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    sanitized_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("* ") or stripped.startswith("- "):
            sanitized_lines.append("\n" + line + "\n")
        else:
            sanitized_lines.append(line)
            
    compiled_text = re.sub(r"\n{3,}", "\n\n", "".join(sanitized_lines))
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(compiled_text.strip() + "\n")
    return True

paths_to_clear = [
    r"C:\Google\CloudSDK\Goings-OS\notebook_sources\implementation_plan.md",
    r"C:\Google\CloudSDK\Goings-OS\core_nodes\node_13_developer\companion_app\implementation_plan.md"
]

# Walk internal cache directories to capture any loose file fragments
cache_root = r"C:\Users\Moxy Medical\.gemini\antigravity-ide\brain"
if os.path.exists(cache_root):
    for root, dirs, files in os.walk(cache_root):
        for file in files:
            if "implementation_plan.md" in file.lower():
                paths_to_clear.append(os.path.join(root, file))

for target in paths_to_clear:
    if repair_markdown_syntax(target):
        print(f"[RECONCILED] Cleaned padding guidelines for: {target}")
