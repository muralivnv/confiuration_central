#!/usr/bin/env python3

import sys
import os
from datetime import datetime
from subprocess import run, DEVNULL

ATTACHMENT_DIR = "attachments"

dir = sys.stdin.read()
dir = dir.strip()

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
except:
    pass

if is_png_creation_success:
    # add this info into file
    text = f"""![]({os.path.join(ATTACHMENT_DIR, png_filename)})"""
    print(text)
    # os.system(f"""echo "{text}" >> {filepath}""")
