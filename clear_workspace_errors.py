import os
import re

def optimize_markdown_file(file_path):
    if not os.path.exists(file_path):
        return False
        
    print(f"[FORMATTING] Processing compliance layout rules for: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Enforce clear vertical blank padding boundaries for headings (MD022)
    content = re.sub(r'(?<!\n)\n(#{1,6} .*)\n', r'\n\n\1\n', content)
    content = re.sub(r'\n(#{1,6} .*)\n(?!\n)', r'\n\1\n\n', content)

    # Enforce clear vertical blank padding boundaries for list elements (MD032)
    content = re.sub(r'(?<!\n)\n([\*\-\+] .*)\n', r'\n\n\1\n', content)
    content = re.sub(r'\n([\*\-\+] .*)\n(?!\n)', r'\n\1\n\n', content)

    # Sanitize and contract excessive whitespace blocks to keep file arrays compact
    clean_content = re.sub(r'\n{3,}', '\n\n', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(clean_content.strip() + "\n")
    return True

# Map local root targets and internal ide cache directories simultaneously
target_locations = [
    r"C:\Google\CloudSDK\Goings-OS\notebook_sources\implementation_plan.md",
    r"C:\Google\CloudSDK\Goings-OS\core_nodes\node_13_developer\companion_app\implementation_plan.md"
]

for target in target_locations:
    success = optimize_markdown_file(target)
    if success:
        print(f"[SUCCESS] File layout successfully anchored to compliance standard: {os.path.basename(target)}")
