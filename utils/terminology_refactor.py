# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# UTILITY: GLOBAL TERMINOLOGY REFACTOR CONTROLLER
# COMPLIANCE: ZERO EM-DASHES // ALWAYS POSITIVE // EXPLICIT TYPING
# ==============================================================================

import os

def execute_global_refactor(root_directory: str) -> None:
    """Crawls the entire workspace drive to align kernel naming conventions."""
    target_terms_lowercase: list = ["private kernel", "private kernel"]
    target_terms_titlecase: list = ["Private Kernel", "Private Kernel"]
    
    corrected_lowercase: str = "private kernel"
    corrected_titlecase: str = "Private Kernel"
    
    print("[INITIALIZING] Starting global codebase vocabulary scan...")
    
    for root, folders, files in os.walk(root_directory):
        # Explicitly protect environment dependencies and git history pools
        if ".git" in root or "venv" in root or "__pycache__" in root:
            continue
            
        for file_name in files:
            # Only scan readable development and documentation formats
            if file_name.endswith((".py", ".md", ".json", ".txt", ".bat", ".ps1")):
                file_path: str = os.path.join(root, file_name)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        file_content: str = f.read()
                    
                    content_modified: bool = False
                    
                    # Inspect and replace lowercase anomalies
                    for term in target_terms_lowercase:
                        if term in file_content:
                            file_content = file_content.replace(term, corrected_lowercase)
                            content_modified = True
                            
                    # Inspect and replace titlecase anomalies
                    for term in target_terms_titlecase:
                        if term in file_content:
                            file_content = file_content.replace(term, corrected_titlecase)
                            content_modified = True
                    
                    # Commit updates back to the disk block if anomalies were found
                    if content_modified:
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(file_content)
                        print(f"[REGENERATED] Aligned terminology inside: {file_path}")
                        
                except Exception:
                    # Guard loop safety against unreadable or empty configurations
                    continue

    print("[SUCCESS] Global refactor complete. Naming architecture is uniform.")

if __name__ == "__main__":
    target_workspace: str = r"C:\Google\CloudSDK\Goings-OS"
    execute_global_refactor(target_workspace)
