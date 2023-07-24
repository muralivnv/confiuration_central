#!/usr/bin/env python3

import sys
import os
from subprocess import check_output

# helper functions
def format_markdown_table(markdown_table):
    # Split the markdown table into rows
    rows = markdown_table.strip().split('\n')

    # Extract the headers and content rows
    headers = [header.strip() for header in rows[0].split('|')[1:-1]]
    content_rows = [[cell.strip() for cell in row.split('|')[1:-1]] for row in rows[2:]]

    # Find the maximum width of each column
    col_widths = [max(len(headers[i]), max(len(row[i]) for row in content_rows)) for i in range(len(headers))]

    # Format the headers
    formatted_headers = "| {} |".format(" | ".join(header.center(col_widths[i]) for i, header in enumerate(headers)))

    # Format the header separator
    header_separator = "|-{}-|".format("-|-".join('-' * width for width in col_widths))

    # Format the content rows
    formatted_rows = ["| {} |".format(" | ".join(cell.center(col_widths[i]) for i, cell in enumerate(row))) for row in content_rows]

    # Combine the formatted table parts
    formatted_table = [formatted_headers, header_separator] + formatted_rows

    return "\n".join(formatted_table)

# main
filepath = sys.stdin.read()
filepath = filepath.strip()
table_config = check_output("xclip -selection clipboard -o", shell=True)
table_config = table_config.decode("utf-8")

splits = table_config.split('x')
rows = (splits[0]).strip()
cols = (splits[1]).strip()

try:
    rows = int(rows)
except Exception as e:
    print(f"improper rows -- {rows}")
    exit(1)

try:
    cols = int(cols)
except Exception as e:
    print(f"improper cols -- {cols}")
    exit(1)

sample_row = "| " * cols
sample_row = f"{sample_row}\n"
header_separation = ("|---" * cols) + "|"

table = f"""
{sample_row}{header_separation}
{sample_row * rows}
"""

table = format_markdown_table(table)

# add this info into file
os.system(f"""echo "{table}" >> {filepath}""")
