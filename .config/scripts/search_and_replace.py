#!/usr/bin/python3

# imports
import subprocess
from argparse import ArgumentParser, RawTextHelpFormatter
import sys

# constants
INTERACTIVE_CMD = 'grep -l {GREP_FLAGS} {QUERY} | fzf --sort --reverse --preview="grep -n --color=always -C 2 {GREP_FLAGS} {QUERY} {}" --preview-window="up,70%:wrap" --ansi --bind="enter:execute(sed {SED_CMD} {}),shift-tab:up,tab:down" --cycle'
NONINTERACTIVE_CMD = "grep -l {GREP_FLAGS} {QUERY} | xargs -I @ sh -c 'sed {SED_CMD} @'"
FZF_ERR_CODE_TO_IGNORE = [0, 1, 130]

def trigger(parsed_args) -> None:
    full_cmd = None
    SED_CMD = parsed_args.SED_CMD.replace("{QUERY}", parsed_args.QUERY)
    SED_CMD = SED_CMD.replace("{REPLACE}", parsed_args.REPLACE)
    if parsed_args.no_interactive:
        full_cmd = NONINTERACTIVE_CMD.replace("{GREP_FLAGS}", parsed_args.GREP_FLAGS)
        full_cmd = full_cmd.replace("{QUERY}", parsed_args.QUERY)
        full_cmd = full_cmd.replace("{SED_CMD}", SED_CMD)
    else:
        full_cmd = INTERACTIVE_CMD.replace("{GREP_FLAGS}", parsed_args.GREP_FLAGS)
        full_cmd = full_cmd.replace("{QUERY}", parsed_args.QUERY)
        full_cmd = full_cmd.replace("{SED_CMD}", SED_CMD)
    try:
        subprocess.check_call(full_cmd, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        if not (e.returncode in FZF_ERR_CODE_TO_IGNORE):
            print(e)

if __name__ == "__main__":
    cli = ArgumentParser(formatter_class=RawTextHelpFormatter)

    cli.add_argument("-grep", type=str, dest="GREP_FLAGS", default="-r -w", help="-r -w", required=False)
    cli.add_argument("-sed", type=str, dest="SED_CMD", default='-i "s/{QUERY}/{REPLACE}/g"', help='-i "s/{QUERY}/{REPLACE}/g"', required=False)

    cli.add_argument("-q", type=str, dest="QUERY", help="QUERY", required=True)
    cli.add_argument("-r", type=str, dest="REPLACE", default="", help="REPLACE", required=False)

    cli.add_argument("-ni", action="store_true", dest="no_interactive", help="no interaction")
    cli.add_argument("--gist", help="""
GREP
    -n               : print line numbers
    -H               : print file name
    -i               : ignore case
    -l               : only-print file names that has matches
    --include \*.ext : match files with this extension
    -w               : match whole word
SED:
    -i    : in-place replace

    [RANGE] s/QUERY/REPLACE/[OPTIONS]
      RANGE
       #,{#} : only match these lines
         $   : to final line
      OPTIONS
        # : number to match and replace every nth match in line
        g : match and replace all
        i : ignore case
        p : print lines that has matches

    [RANGE] d : delete lines in this range
      RANGE
       #,{#} : only match these lines
         $   : to final line
    """, required=False)

    parsed_args = cli.parse_args()
    print(parsed_args)

    trigger(parsed_args)
