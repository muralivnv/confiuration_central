#!/usr/bin/env python3

import sys
import os
from datetime import datetime

# Config
ATTACHMENT_DIR = "attachments"

# main
filepath = sys.stdin.read()
filepath = filepath.strip()
if not any(filepath):
    print("[ERROR] filepath is empty")
    exit(1)
dir, _ = os.path.split(filepath)

# create png file-path
folder = os.path.join(dir, ATTACHMENT_DIR)
os.makedirs(folder, exist_ok=True)

png_filename = f'{datetime.now():%Y-%m-%d_%H_%M_%S%z}.png'
png_filepath = os.path.join(folder, png_filename)

# output to file
is_png_creation_success = False
try:
    retcode = os.system(f"xclip -selection clipboard -t image/png -o > {png_filepath}")
    if (retcode == 0):
        is_png_creation_success = True
except Exception as e:
    print(e)
    exit(1)

if is_png_creation_success:
    # add this info into file
    text = f"""![]({os.path.join(ATTACHMENT_DIR, png_filename)})"""
    os.system(f"""echo "{text}" >> {filepath}""")
