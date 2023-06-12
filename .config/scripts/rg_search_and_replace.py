#!/usr/bin/python3

# imports
import subprocess
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import sys

# constants
INTERACTIVE_CMD = '{RG_BASE_CMD} -l | fzf --sort --reverse --preview="{RG_BASE_CMD} --color=always -C 2 {}" --preview-window="up,70%:wrap" --ansi --bind="enter:execute({RG_BASE_CMD} --passthru {} > {}.temp && mv {}.temp {}),shift-tab:up,tab:down" --cycle'
NONINTERACTIVE_CMD = "{RG_BASE_CMD} -l | xargs -I @ sh -c '{RG_BASE_CMD} --passthru @ > @.temp && mv @.temp @' "
FZF_ERR_CODE_TO_IGNORE = [0, 1, 130]

# helper functions
def create_rg_base_cmd(parsed_args) -> str:
    out = f"rg {parsed_args.query} {parsed_args.rg_opt} "
    if any(parsed_args.replace):
        out = f"{out} -r {parsed_args.replace} "
    return out

def trigger(parsed_args) -> None:
    rg_base_cmd = create_rg_base_cmd(parsed_args)
    full_cmd = None
    if parsed_args.no_interactive:
        full_cmd = NONINTERACTIVE_CMD.replace("{RG_BASE_CMD}", rg_base_cmd)
    else:
        full_cmd = INTERACTIVE_CMD.replace("{RG_BASE_CMD}", rg_base_cmd)
    try:
        subprocess.check_call(full_cmd, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        if not (e.returncode in FZF_ERR_CODE_TO_IGNORE):
            print(e)

if __name__ == "__main__":
    cli = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    cli.add_argument("-c", "--rg-opt", type=str, help="ripgrep options", dest="rg_opt", default="-S -w", required=False)
    cli.add_argument("-ni", "--no-interactive", action="store_true", dest="no_interactive")
    cli.add_argument("-q", "--query", type=str, required=True, dest="query", help="pattern to search")
    cli.add_argument("-r", "--replace", type=str, required=False, dest="replace", help="replace with", default="")
    parsed_args = cli.parse_args()

    trigger(parsed_args)
