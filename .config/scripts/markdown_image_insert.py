#!/usr/bin/env python3

import sys
import os
from datetime import datetime
from subprocess import run, PIPE, CalledProcessError

# Config
ATTACHMENT_DIR = "attachments"

# main
filepath = sys.stdin.read()
filepath = filepath.strip()
if not any(filepath):
    print("[ERROR] filepath is empty")
    exit(1)
dir, _ = os.path.split(filepath)

# Get the clipboard data and its type
try:
    clipboard_data = run(["xclip", "-selection", "clipboard", "-o", "-t", "TARGETS"],
                         check=True, stdout=PIPE, stderr=PIPE, text=True)
    data_type = run(["grep", "-o", "image/png"], input=clipboard_data.stdout, check=True, stdout=PIPE,
                    stderr=PIPE, text=True)
except CalledProcessError:
    print("[ERROR] clipboard does not contain any image info")
    exit(1)

# Check if the clipboard contains image data in PNG format
if not data_type.stdout.strip():
    print("[ERROR] clipboard does not contain any image info")
    exit(1)
else:
    # create png file-path
    try:
        completed_process = run(["xclip", "-selection", "clipboard", "-t", "image/png", "-o"],
                                 stdout=PIPE, stderr=PIPE, check=True)

        folder = os.path.join(dir, ATTACHMENT_DIR)
        os.makedirs(folder, exist_ok=True)

        png_filename = f'{datetime.now():%Y-%m-%d_%H_%M_%S%z}.png'
        png_filepath = os.path.join(folder, png_filename)

        with open(png_filepath, "wb") as f:
            f.write(completed_process.stdout.strip())
        text = f"""![]({os.path.join(ATTACHMENT_DIR, png_filename)})"""
        print(text)
    except CalledProcessError:
        print("[ERROR] An error occurred while saving the image data.")
        exit(1)
