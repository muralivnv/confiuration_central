#!/usr/bin/python3

# imports
import subprocess
from argparse import ArgumentParser, RawTextHelpFormatter
import sys

##### HELPFUL GIST
GIST = """
GREP: https://www.man7.org/linux/man-pages/man1/grep.1.html
    -n               : print line numbers
    -H               : print file name
    -i               : ignore case
    -l               : only-print file names that has matches
    --include \*.ext : match files with this extension
    -w               : match whole word
    -E               : extended regexp
    -r               : recursive

SED: https://www.gnu.org/software/sed/manual/sed.html
    -i    : in-place replace
    -n    : silent-mode
    -E    : extended regexp

    [ADDR] s/QUERY/REPLACE/[OPTIONS]
      ADDR
       #,{{#}}  : only match these lines
         $      : to final line
       /REGEXP/ : Any regexp
       /REGEXP/,/REGEXP/ : range using regexp

      OPTIONS
        # : number to match and replace every nth match in line
        g : match and replace all
        i : ignore case
        p : print lines that has matches

    [ADDR] [X]
      ADDR
       #,{{#}}  : only match these lines
         $      : to final line
       /REGEXP/ : Any regexp
       /REGEXP/,/REGEXP/ : range using regexp

      [X]
       i\TEXT  : insert text before line
       c\TEXT  : replace line with this text
       a\TEXT  : append text after line
       p       : print
       d       : delete
       q       : quit

   \\u : turn next char to upper
   \\U : turn next replacement to upper case
   \\l : turn next char to lower
   \\L : turn next replacement to lower case
   \\E : end conversion started by above

   If we wrap search items inside () then we can use \\number (0 to 9)
   sar -q "(\w*)\s*([:=])\s*(true|[0-9]{4})" --sed "'s/{QUERY}/\\U\\1 \E\\u\\2\E \\3/g'"
Combining Multiple Files Using SED:
    sed '$ s/$//' FILE1 FILE2 FILE3 ... > OUTFILE
"""

# constants
INTERACTIVE_CMD = """grep -l {GREP_FLAGS} "{QUERY}" | fzf --sort --reverse --preview='grep -n --color=always -C 2 {GREP_FLAGS} "{QUERY}" {}' --preview-window='up,70%:wrap' --ansi --bind="enter:execute(sed {SED_CMD} {})+refresh-preview,shift-tab:up,tab:down" --cycle"""
NONINTERACTIVE_CMD = """grep -l {GREP_FLAGS} "{QUERY}" | xargs -I {} sh -c "sed {SED_CMD} {}" """
FZF_ERR_CODE_TO_IGNORE = [0, 1, 130]

#####
def trigger(parsed_args) -> None:
    full_cmd = None
    SED_CMD = parsed_args.SED_CMD.replace("{QUERY}", parsed_args.QUERY)
    SED_CMD = SED_CMD.replace("{Q}", parsed_args.QUERY) # short-form
    SED_CMD = SED_CMD.replace("{REPLACE}", parsed_args.REPLACE)
    SED_CMD = SED_CMD.replace("{R}", parsed_args.REPLACE) # short-form
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

    cli.add_argument("-g", "--grep", type=str, dest="GREP_FLAGS", default="-r -w", help="-r -w", required=False)
    cli.add_argument("-s", "--sed", type=str, dest="SED_CMD", default="-i 's/{QUERY}/{REPLACE}/g'", help="-i 's/{QUERY}|{Q}/{REPLACE}|{R}/g'", required=False)

    cli.add_argument("-ni", action="store_true", dest="no_interactive", help="no interaction")
    cli.add_argument("--gist", "--man", action="store_true", dest="show_gist", help="show some gist", required=False)

    cli.add_argument("QUERY", type=str, nargs="?", default="")
    cli.add_argument("REPLACE", type=str, nargs="?", default="")

    parsed_args = cli.parse_args()
    if parsed_args.show_gist:
        cli.print_help()
        print(GIST)
        sys.exit(0)

    if not any(parsed_args.QUERY):
        raise ValueError("empty QUERY specified")
        sys.exit(0)

    trigger(parsed_args)
