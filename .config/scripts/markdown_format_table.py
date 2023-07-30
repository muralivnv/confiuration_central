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

table = check_output("xclip -selection clipboard -o", shell=True)
table = table.decode("utf-8")
table = table.strip()
if not any(table):
    print("[ERROR] table is empty")
    exit(1)

try:
    table = format_markdown_table(table)
except Exception as e:
    print(e)
    exit(1)

# add this info into file
print(table)