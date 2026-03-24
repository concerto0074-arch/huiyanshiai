import glob
import re

files = glob.glob('d:\\huiyanshiai(2.0)\\frontend\\*.html')
count = 0
for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    curr_content = content
    # Common formats of the copyright footer string
    content = re.sub(r'© 2024 慧眼识癌', r'© 2025 慧眼识癌', content)
    content = re.sub(r'&copy; 2024 慧眼识癌', r'&copy; 2025 慧眼识癌', content)
    
    if curr_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1

print(f"Updated copyright year to 2025 in {count} HTML files.")
