#!/usr/bin/env python3

import sys
import os
from subprocess import check_output

# helper functions
# NOTE: too-lazy to write hence Chat-GPT generated this
def format_markdown_table(markdown_table):
    # Split the markdown table into rows
    rows = markdown_table.strip().split('\n')

    # Extract the headers and content rows
    headers = [header.strip() for header in rows[0].split('|')[1:-1]]
    content_rows = [[cell.strip() for cell in row.split('|')[1:-1]] for row in rows[2:]]

    # Find the maximum width of each column
    col_widths = [max(len(headers[i]), max(len(row[i]) for row in content_rows)) for i in range(len(headers))]

    # Ensure the header separator has at least three dashes '---' for each column
    header_separator = "|-" + "-|-".join(['-' * max(col_widths[i], 3) for i in range(len(headers))]) + "-|"

    # Format the headers
    formatted_headers = "| {} |".format(" | ".join(header.center(max(col_widths[i], 3)) for i, header in enumerate(headers)))

    # Format the content rows
    formatted_rows = ["| {} |".format(" | ".join(cell.center(max(col_widths[i], 3)) for i, cell in enumerate(row))) for row in content_rows]

    # Combine the formatted table parts
    formatted_table = [formatted_headers, header_separator] + formatted_rows

    return "\n".join(formatted_table)

# main
filepath = sys.stdin.read()
filepath = filepath.strip()
if not any(filepath):
    print("[ERROR] filepath is empty")
    exit(1)

table_config = check_output("xclip -selection clipboard -o", shell=True)
table_config = table_config.decode("utf-8")

if not any(table_config) or not ('x' in table_config):
    print("[ERROR] specified table_config is faulty")
    exit(1)

splits = table_config.split('x')
if len(splits) != 2:
    print("[ERROR] table_config contains more than 2 items")
    exit(1)

rows = (splits[0]).strip()
cols = (splits[1]).strip()

try:
    rows = int(rows)
except Exception as e:
    print(f"[ERROR] cannot parse n-rows as int -- {rows}")
    exit(1)

try:
    cols = int(cols)
except Exception as e:
    print(f"[ERROR] cannot parse n-cols as int -- {cols}")
    exit(1)

sample_row = "| " * cols
sample_row = f"{sample_row}\n"
header_separation = ("|---" * cols) + "|"

table = f"""
{sample_row}{header_separation}
{sample_row * rows}
"""

try:
    table = format_markdown_table(table)
except Exception as e:
    print(e)
    exit(1)

# add this info into file
print(table)
