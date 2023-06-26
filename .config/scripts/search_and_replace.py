#!/usr/bin/python3

# imports
import subprocess
from argparse import ArgumentParser, RawTextHelpFormatter
import sys
import os
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
GREP_CMD = """grep -l -m1 {GREP_FLAGS} "{QUERY}" """

INTERACTIVE_CMD = """fzf --sort --color hl:221,hl+:74 --scrollbar=▌▐ --reverse --preview='sed {SED_CMD} {} > {}.SAR_OUT && git diff --color {} {}.SAR_OUT | tail -n +5' --preview-window='up,70%:wrap' --ansi --bind='enter:execute(mv {}.SAR_OUT {})+refresh-preview,shift-tab:up,tab:down' --cycle"""

NONINTERACTIVE_CMD = """xargs -I {} sh -c 'sed -i {SED_CMD} {}' """

FZF_ERR_CODE_TO_IGNORE = [0, 1, 130]
GREP_DEFAULTS = ["-l", "-m1", "-r", "--exclude-dir=\.*", "--exclude-dir=*build*", "--exclude=*\.SAR_OUT"]

#####
def wrap_in_word_boundary(text: str)->str:
    return "\<" + text + "\>"

def prepare_grep_cmd(grep_flags: List[str], query: str) -> List[str]:
    new_grep_flags = []
    for i, flag in enumerate(grep_flags):
        stripped_flag = flag.strip()
        if any(stripped_flag):
            splits = stripped_flag.split(' ')
            new_grep_flags.extend(splits)
    grep_cmd = ["grep"] + new_grep_flags + [query]
    return grep_cmd

def trigger(parsed_args) -> None:
    # assemble grep
    grep_flags = parsed_args.GREP_FLAGS
    if any(parsed_args.ADDITIONAL_GREP_FLAGS):
        grep_flags.extend(parsed_args.ADDITIONAL_GREP_FLAGS)
    if parsed_args.match_whole_word_only:
        grep_flags.append("-w")
    grep_cmd = prepare_grep_cmd(grep_flags, parsed_args.QUERY)

   # assemble sed
    sed_query = parsed_args.QUERY
    if parsed_args.match_whole_word_only:
        sed_query = wrap_in_word_boundary(sed_query)
    sed_cmd = parsed_args.SED_CMD.replace("{QUERY}", sed_query)
    sed_cmd = sed_cmd.replace("{Q}", sed_query) # short-form

    full_cmd = INTERACTIVE_CMD
    if parsed_args.no_interactive:
        full_cmd = NONINTERACTIVE_CMD

    full_cmd = full_cmd.replace("{SED_CMD}"   , sed_cmd)
    full_cmd = full_cmd.replace("{QUERY}"     , parsed_args.QUERY)
    full_cmd = full_cmd.replace("{Q}"         , parsed_args.QUERY) # short-form

    query_files: List[str] = []
    try:
        # get list of files that query exists using GREP
        foi = subprocess.Popen(grep_cmd,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        query_files = foi.stdout.read()
        res = foi.communicate()
        if (foi.returncode != 0):
            error = res[1].strip()
            if not any(error):
                error = "QUERY matched nothing"
            print("[ERROR] -- ", error)
            print("[CMD] -- ", grep_cmd)
            return

        # pass it through next command
        subprocess.run(full_cmd,
                     shell=True, input=query_files, universal_newlines=True)

        # store query files for post-processing
        query_files = query_files.split('\n')

    except subprocess.CalledProcessError as e:
        if not (e.returncode in FZF_ERR_CODE_TO_IGNORE):
            print(e)
    except Exception as e:
        print(e)

    if any(query_files):
        for file in query_files:
            if os.path.exists(f"{file}.SAR_OUT"):
                os.system(f"rm {file}.SAR_OUT")

if __name__ == "__main__":
    cli = ArgumentParser(formatter_class=RawTextHelpFormatter)
    cli.add_argument("-g", type=str, dest="GREP_FLAGS", nargs="*", default=GREP_DEFAULTS, help=' '.join(GREP_DEFAULTS), required=False)
    cli.add_argument("-g+", type=str, dest="ADDITIONAL_GREP_FLAGS", nargs="*", default=[], required=False)
    cli.add_argument("-s", type=str, dest="SED_CMD", default="", help="sed command", required=not "--gist" in sys.argv)

    cli.add_argument("-ni", action="store_true", dest="no_interactive", help="no interaction")
    cli.add_argument("-w", action="store_true", dest="match_whole_word_only", help="restrict match to whole words")

    cli.add_argument("--gist", action="store_true", dest="show_gist", help="show some gist", required=False)

    cli.add_argument("QUERY", type=str, nargs="?", default="")

    parsed_args = cli.parse_args()
    if parsed_args.show_gist:
        cli.print_help()
        print(GIST)
        sys.exit(0)

    if not any(parsed_args.QUERY):
        raise ValueError("empty QUERY specified")
        sys.exit(0)

    trigger(parsed_args)
