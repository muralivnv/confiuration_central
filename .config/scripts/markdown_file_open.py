#!/usr/bin/env python3

import sys
import os
from subprocess import check_output
from time import sleep
import re

def parse_markdown_file_ref(markdown_text, dir):
    # Regular expression to match Markdown image syntax
    image_regex = r"!\[.*?\]\((.*?)\)"

    # Find all occurrences of the image syntax in the text
    image_matches = re.findall(image_regex, markdown_text)

    # Initialize lists to store image paths and local file references
    image_paths = []
    local_file_references = []

    for match in image_matches:
        # Check if the image reference is a local file
        if match.startswith("file://"):
            local_file_references.append(match[len("file://"):])
        else:
            image_paths.append(match)

    for image in image_paths:
        image = os.path.join(dir, image)
        image = image.replace("%20", "\ ") # to take of obsidian insertion syntax
        os.system(f"xdg-open {image}")
        sleep(0.3)

# main
filepath = sys.stdin.read()
filepath = filepath.strip()
dir, _ = os.path.split(filepath)

selection = check_output("xclip -selection clipboard -o", shell=True)
selection = selection.decode("utf-8")
selection = selection.strip()

parse_markdown_file_ref(selection, dir)
