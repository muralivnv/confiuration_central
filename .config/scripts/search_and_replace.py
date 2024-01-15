#!/usr/bin/python3

# imports
import subprocess
import shutil
from argparse import ArgumentParser, Namespace
import sys
import os
from typing import List

# HELPFUL GIST
GIST = r"""
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
INTERACTIVE_CMD = """fzf --sort --color hl:bright-yellow,hl+:bright-red --scrollbar=▌▐ --reverse --preview='sed {SED_CMD} {} > {}.SAR_OUT && diff -u --color=always --palette=":de=1;31:ad=1;32" {} {}.SAR_OUT | tail -n +3' --preview-window='up,70%:wrap' --ansi --bind='enter:execute(mv {}.SAR_OUT {})+refresh-preview,shift-tab:up,tab:down' --cycle"""
NONINTERACTIVE_CMD = """xargs -I {{}} sh -c 'sed -i {SED_CMD} {{}} && echo "MODIFIED -- {{}}"' """
FZF_ERR_CODE_TO_IGNORE = [0, 1, 130]
GREP_DEFAULTS          = ["-l", "-m1", "-r", "--exclude-dir=\.*", "--exclude-dir=*build*", "--exclude=*\.SAR_OUT"]

NONE_STR = "__$%^NONE^%$__"
BACKUP_DIR = ".sar_last_change"
#####

def get_clipboard_data() -> str:
    p = subprocess.Popen(["xclip","-selection", "clipboard", "-o"],
                        stdout=subprocess.PIPE)
    p.wait()
    data = p.stdout.read()
    data = data.decode("utf-8")
    return data

def wrap_in_word_boundary(text: str, use_extended_regexp: bool)->str:
    if use_extended_regexp:
        return r"\<(" + text + r")\>"
    else:
        return r"\<" + text + r"\>"

def prepare_grep_cmd(parsed_args: Namespace) -> List[str]:
    grep_flags = parsed_args.GREP_FLAGS
    if any(parsed_args.ADDITIONAL_GREP_FLAGS):
        grep_flags.extend(parsed_args.ADDITIONAL_GREP_FLAGS)
    if parsed_args.match_whole_word_only:
        grep_flags.append("-w")
    if parsed_args.use_extended_regexp:
        grep_flags.append("-E")

    # remove extra spaces around each grep flag if any
    new_grep_flags = []
    for flag in grep_flags:
        stripped_flag = flag.strip()
        if any(stripped_flag):
            splits = stripped_flag.split(" ")
            new_grep_flags.extend(splits)
    grep_cmd = ["grep"] + new_grep_flags + [parsed_args.QUERY]
    return grep_cmd

def prepare_sed_cmd(parsed_args: Namespace) -> str:
    sed_query = parsed_args.QUERY
    sed_replace = parsed_args.REPLACE
    sed_cmd = parsed_args.SED_CMD

    sed_query_wrapped = sed_query
    if parsed_args.match_whole_word_only:
        sed_query_wrapped = wrap_in_word_boundary(sed_query, parsed_args.use_extended_regexp)
    if parsed_args.use_extended_regexp:
        sed_cmd = "-E " + sed_cmd

    sed_cmd = sed_cmd.replace("{QUERY}", sed_query_wrapped)
    sed_cmd = sed_cmd.replace("{Q}", sed_query_wrapped) # short-form

    sed_replace = sed_replace.replace("{QUERY}", sed_query)
    sed_replace = sed_replace.replace("{Q}", sed_query)
    sed_cmd = sed_cmd.replace("{REPLACE}", sed_replace)
    sed_cmd = sed_cmd.replace("{R}", sed_replace) # short-form
    return sed_cmd

def delete_temporary_files(files: List[str]) -> None:
    if any(files):
        for file in files:
            if os.path.exists(f"{file}.SAR_OUT"):
                os.system(f"rm {file}.SAR_OUT")

def make_backup(grep_output: str):
    backup_dir = os.path.join(os.getcwd(), BACKUP_DIR)
    os.makedirs(backup_dir, exist_ok=True)

    query_files = grep_output.split("\n")
    for file_path in query_files:
        file_path = file_path.strip()
        if any(file_path):
            path, _ = os.path.split(file_path)
            dest = backup_dir
            if any(path):
                dest = os.path.join(backup_dir, path)
                os.makedirs(dest, exist_ok=True)
            shutil.copy2(file_path, dest)

def trigger(parsed_args: Namespace) -> None:
    grep_cmd = prepare_grep_cmd(parsed_args)
    sed_cmd  = prepare_sed_cmd(parsed_args)

    full_cmd = INTERACTIVE_CMD
    if parsed_args.no_interactive:
        full_cmd = NONINTERACTIVE_CMD

    full_cmd = full_cmd.replace("{SED_CMD}", sed_cmd)

    query_files: List[str] = []
    try:
        # get list of files that query exists using GREP
        foi = subprocess.Popen(grep_cmd,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        grep_output: str = foi.stdout.read()
        res = foi.communicate()
        if foi.returncode != 0:
            error = res[1].strip()
            if not any(error):
                error = "QUERY matched nothing"
            print("[ERROR] -- ", error)
            print("[CMD] -- ", grep_cmd)
            return

        make_backup(grep_output)

        # pass it through next command
        subprocess.run(full_cmd,
                       shell=True, input=grep_output, universal_newlines=True)

        # store query files for post-processing
        query_files = grep_output.split("\n")

    except subprocess.CalledProcessError as e:
        if not e.returncode in FZF_ERR_CODE_TO_IGNORE:
            print(e)
    except Exception as e:
        print(e)
    finally:
        delete_temporary_files(query_files)

def revert_last_change():
    dest = os.getcwd()
    src = os.path.join(dest, BACKUP_DIR)

    for root, _, files in os.walk(src):
        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(dest, os.path.relpath(source_file, src))
            shutil.move(source_file, dest_file)
            print("\n--- CHANGES UNDONE: ", dest_file)

if __name__ == "__main__":
    cli = ArgumentParser()
    cli.add_argument("-g", type=str, dest="GREP_FLAGS", nargs="*", default=GREP_DEFAULTS, help=" ".join(GREP_DEFAULTS), required=False)
    cli.add_argument("-g+", type=str, dest="ADDITIONAL_GREP_FLAGS", nargs="*", default=[], required=False)
    cli.add_argument("-s", type=str, dest="SED_CMD", default="", help="sed command",
                     required="--gist" not in sys.argv and "--undo" not in sys.argv)

    cli.add_argument("-ni", action="store_true", dest="no_interactive", help="no interaction")
    cli.add_argument("-w", action="store_true", dest="match_whole_word_only", help="restrict match to whole words")
    cli.add_argument("-E", action="store_true", dest="use_extended_regexp", help="turn on extended regexp mode")

    cli.add_argument("--gist", action="store_true", dest="show_gist", help="show some gist", required=False)

    cli.add_argument("--undo", action="store_true", dest="undo_last_change", help="Undo last change",
                     required=False)

    cli.add_argument("QUERY", type=str, nargs="?", default=NONE_STR)
    cli.add_argument("REPLACE", type=str, nargs="?", default=NONE_STR)

    parsed_args = cli.parse_args()
    if parsed_args.show_gist:
        cli.print_help()
        print(GIST)
        sys.exit(0)

    if parsed_args.undo_last_change:
        revert_last_change()
    else:
        if parsed_args.QUERY == NONE_STR:
            parsed_args.QUERY = get_clipboard_data()
            print("Using clipboard item as QUERY -- ", parsed_args.QUERY)

        if not any(parsed_args.QUERY):
            raise ValueError("QUERY is empty")

        if parsed_args.REPLACE == NONE_STR:
            parsed_args.REPLACE = parsed_args.QUERY

        trigger(parsed_args)
