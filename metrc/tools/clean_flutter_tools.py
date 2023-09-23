"""
Clean Flutter Tools
Copyright (c) 2021-2023 Cannlytics

Authors:
    Keegan Skeate <https://github.com/keeganskeate>
Created: 2/20/2023
Updated: 2/20/2023
License: MIT License <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>

Description: Remove temporary Flutter tools from the user temp directory.

Command-line example:

    ```
    python app/tools/clean_flutter_tools
    ```
"""
# Standard imports:
import os
import shutil

def clean_flutter_tools():
    """Removes excessive Flutter tools directories from user's `temp`.
    See: https://github.com/flutter/flutter/issues/84094
    """
    temp_dir = os.path.join(os.environ.get('TEMP'), '')
    for dir_name in os.listdir(temp_dir):
        if dir_name.startswith('flutter_tools.'):
            full_dir_path = os.path.join(temp_dir, dir_name)
            try:
                shutil.rmtree(full_dir_path)
                print(f"Successfully removed directory {full_dir_path}")
            except OSError as e:
                print(f"Error removing directory {full_dir_path}: {e}")

# === Test ===
if __name__ == '__main__':
    clean_flutter_tools()
