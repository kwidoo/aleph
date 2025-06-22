import os
import re
import json
from typing import Dict, List

class TranslationManager:
    def __init__(self, source_dir: str, output_file: str):
        self.source_dir = source_dir
        self.output_file = output_file

    def extract_translation_keys(self) -> Dict[str, List[str]]:
        """Extract translation keys from Python files."""
        keys = {}
        pattern = re.compile(r'_\("(.*?)"\)')  # Matches _("key")

        for root, _, files in os.walk(self.source_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = pattern.findall(content)
                        if matches:
                            keys[file_path] = matches

        return keys

    def save_keys_to_file(self, keys: Dict[str, List[str]]):
        """Save extracted keys to a JSON file."""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(keys, f, indent=4, ensure_ascii=False)

    def detect_unused_keys(self, keys: Dict[str, List[str]], translations: Dict[str, str]) -> List[str]:
        """Detect unused translation keys."""
        unused_keys = [key for key in translations if key not in keys]
        return unused_keys

if __name__ == "__main__":
    source_directory = "./src"
    output_file = "./translations/keys.json"

    manager = TranslationManager(source_directory, output_file)
    extracted_keys = manager.extract_translation_keys()
    manager.save_keys_to_file(extracted_keys)

    print(f"Extracted keys saved to {output_file}")
