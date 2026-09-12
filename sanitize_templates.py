import os

root_directory = r"C:\Google\CloudSDK\Goings-OS"
print("[SYSTEM] Executing comprehensive Private Governor template alignment sweep.")

for root, dirs, files in os.walk(root_directory):
    if ".venv" in root or ".git" in root:
        continue
    for file in files:
        if file.endswith(('.py', '.md', '.json', '.toml', '.txt', '.html')):
            target_path = os.path.join(root, file)
            try:
                with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                    file_data = f.read()
                
                if "Private Governor" in file_data.lower() or "private_governor" in file_data.lower():
                    print(f"[ALIGNMENT] Updating terminology in configuration resource: {file}")
                    file_data = file_data.replace("Private Governor", "Private Governor")
                    file_data = file_data.replace("Private Governor", "Private Governor")
                    file_data = file_data.replace("private_governor", "private_governor")
                    file_data = file_data.replace("Private_Governor", "Private_Governor")
                    
                    with open(target_path, "w", encoding="utf-8") as f:
                        f.write(file_data)
            except Exception:
                pass
print("[SUCCESS] Template sanitization pass complete.")
