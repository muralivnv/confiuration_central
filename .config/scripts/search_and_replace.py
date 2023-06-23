#!/usr/bin/python3

# imports
import subprocess
from argparse import ArgumentParser, RawTextHelpFormatter
import sys
from typing import List

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
INTERACTIVE_CMD = """grep -l {GREP_FLAGS} "{QUERY}" | fzf --sort --color hl:221,hl+:74 --scrollbar=▌▐ --reverse --preview='grep -n --color=always -C 2 {GREP_FLAGS} "{QUERY}" {}' --preview-window='up,70%:wrap' --ansi --bind="enter:execute(sed {SED_CMD} {})+refresh-preview,shift-tab:up,tab:down" --cycle"""
NONINTERACTIVE_CMD = """grep -l {GREP_FLAGS} "{QUERY}" | xargs -I {} sh -c "sed {SED_CMD} {}" """
FZF_ERR_CODE_TO_IGNORE = [0, 1, 130]
GREP_DEFAULTS = "-r --exclude-dir=\.* --exclude-dir=*build*"
SED_DEFAULTS  = "-i"

#####
class ArgGroup:
    def __init__(self):
        self.start = None
        self.len   = None
        self.is_initialized = False

    def init(self, i : int):
        self.start = i + 1
        self.len   = 0
        self.is_initialized = True

    def inc(self):
        if self.is_initialized:
            self.len += 1

    def reset(self):
        self.start = None
        self.len = None
        self.is_initialized = False

    def require_grouping(self):
        return self.is_initialized

    def group(self, args: List[str]):
        grouped_args = ' '.join(args[self.start:self.start + self.len])
        if (not grouped_args.startswith(' ')) and (not grouped_args.endswith(' ')):
            grouped_args = f" {grouped_args}"
        return grouped_args

def trigger(parsed_args) -> None:
    query = parsed_args.QUERY
    if parsed_args.match_whole_word_only:
        query = "\<" + query
        query = query + "\>"

    grep_flags = parsed_args.GREP_FLAGS
    if not (parsed_args.ADDITIONAL_GREP_FLAGS is None):
        grep_flags = f"{grep_flags} {parsed_args.ADDITIONAL_GREP_FLAGS}"
    if parsed_args.match_whole_word_only:
        grep_flags = f"{grep_flags} -w"

    sed_flags = parsed_args.SED_FLAGS
    if not (parsed_args.ADDITIONAL_SED_FLAGS is None):
        sed_flags = f"{sed_flags} {parsed_args.ADDITIONAL_SED_FLAGS}"

    full_cmd = INTERACTIVE_CMD
    if parsed_args.no_interactive:
        full_cmd = NONINTERACTIVE_CMD

    full_cmd = full_cmd.replace("{GREP_FLAGS}", grep_flags)
    full_cmd = full_cmd.replace("{SED_CMD}"   , sed_flags)
    full_cmd = full_cmd.replace("{QUERY}"     , query)
    full_cmd = full_cmd.replace("{Q}"         , query) # short-form
    try:
        subprocess.check_call(full_cmd, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        if not (e.returncode in FZF_ERR_CODE_TO_IGNORE):
            print(e)

def group_args(args: List[str]):
    flags_of_interest = ["-g", "--grep", "-g+", "--grep+", "-s", "--sed",
                         "-s+", "--sed+"]
    flags_of_not_interest = ["-w", "-ni", "--gist", "--man"]

    arg_grouper = ArgGroup()
    new_args = []

    for i, arg in enumerate(args):
        if arg in flags_of_not_interest:
            if arg_grouper.require_grouping():
                new_args.append(arg_grouper.group(args))
                arg_grouper.reset()

            new_args.append(arg)
        elif arg in flags_of_interest:
            if arg_grouper.require_grouping():
                new_args.append(arg_grouper.group(args))
                arg_grouper.reset()

            new_args.append(arg)
            arg_grouper.init(i)
        else:
            if arg_grouper.is_initialized:
                arg_grouper.inc()
            else:
                new_args.append(arg)

    if arg_grouper.require_grouping():
        new_args.append(arg_grouper.group(args))
    return new_args

if __name__ == "__main__":
    cli = ArgumentParser(formatter_class=RawTextHelpFormatter)
    cli.add_argument("-g", "--grep", type=str, dest="GREP_FLAGS", default=GREP_DEFAULTS, help=GREP_DEFAULTS, required=False)
    cli.add_argument("-g+", "--grep+", type=str, dest="ADDITIONAL_GREP_FLAGS", required=False)

    cli.add_argument("-s", "--sed", type=str, dest="SED_FLAGS", default=SED_DEFAULTS, help=SED_DEFAULTS, required=False)
    cli.add_argument("-s+", "--sed+", type=str, dest="ADDITIONAL_SED_FLAGS", required=False)

    cli.add_argument("-ni", action="store_true", dest="no_interactive", help="no interaction")
    cli.add_argument("-w", action="store_true", dest="match_whole_word_only", help="don't restrict match to whole words")
    cli.add_argument("--gist", "--man", action="store_true", dest="show_gist", help="show some gist", required=False)

    cli.add_argument("QUERY", type=str, nargs="?", default="")

    args = group_args(sys.argv[1:])
    parsed_args = cli.parse_args(args)
    if parsed_args.show_gist:
        cli.print_help()
        print(GIST)
        sys.exit(0)

    if not any(parsed_args.QUERY):
        raise ValueError("empty QUERY specified")
        sys.exit(0)

    trigger(parsed_args)
