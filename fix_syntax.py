#!/usr/bin/env python3
"""
Fix syntax errors in app_ews.py
"""
import re

# Read the file with UTF-8 encoding
with open('app_ews.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all f-string issues with missing closing quotes
content = re.sub(r"f'([^']*?)\)", r"f'\1'", content)
content = re.sub(r"([^']*?)\)", r"\1'", content)

# Write back the fixed content
with open('app_ews.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed f-string syntax errors in app_ews.py")
