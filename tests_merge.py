import os
import glob
from pathlib import Path

def merge_brandejs_files():
    # Ensure tests directory exists
    tests_dir = Path('tests')
    if not tests_dir.exists():
        print("Error: 'tests' directory not found")
        return False
    
    # Get all .brandejs files in the tests directory
    brandejs_files = glob.glob(str(tests_dir / '*.brandejs'))
    
    if not brandejs_files:
        print("No .brandejs files found in tests directory")
        return False
    
    # Create merged content
    merged_content = []
    for file_path in sorted(brandejs_files):  # Sort to ensure consistent order
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                merged_content.append(content)
                print(f"Successfully read: {file_path}")
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            return False
    
    # Write merged content to output file
    output_path = tests_dir / 'merged.brandejs'
    try:
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write('\n'.join(merged_content))
        print(f"Successfully created merged file: {output_path}")
        return True
    except Exception as e:
        print(f"Error writing merged file: {str(e)}")
        return False

if __name__ == "__main__":
    success = merge_brandejs_files()
    if not success:
        exit(1)