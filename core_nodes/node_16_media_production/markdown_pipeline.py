# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: MARKDOWN DOCUMENT SEGMENTATION PIPELINE
# BIND: NODE 16 MEDIA PRODUCTION // ASSET PIPELINE
# COMPLIANCE: ZERO EM-DASHES ENFORCED // ALWAYS POSITIVE // EXPLICIT TYPING
# ==============================================================================

import os
from pathlib import Path

class MarkdownPipeline:
    def __init__(self, output_dir: str = "data/partitioned_blocks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def segment_file(self, source_file_path: str, chunk_word_count: int = 500) -> list:
        with open(source_file_path, "r", encoding="utf-8") as f:
            words = f.read().split()

        partitioned_paths = []
        chunk_index = 1
        
        for i in range(0, len(words), chunk_word_count):
            chunk_words = words[i:i + chunk_word_count]
            chunk_content = " ".join(chunk_words)
            
            block_title = f"BLOCK_00{chunk_index}" if chunk_index < 10 else f"BLOCK_0{chunk_index}"
            markdown_structure = f"# {block_title}\n\n{chunk_content}\n"
            
            target_file = self.output_dir / f"block_{chunk_index}.md"
            with open(target_file, "w", encoding="utf-8") as out_f:
                out_f.write(markdown_structure)
                
            partitioned_paths.append(str(target_file))
            chunk_index += 1
            
        return partitioned_paths
