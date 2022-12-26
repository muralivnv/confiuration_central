#!/usr/bin/python3

# imports
import subprocess
from argparse import ArgumentParser
import sys

# constants
INTERACTIVE_CMD = '{RG_BASE_CMD} -l | fzf --sort --reverse --preview="{RG_BASE_CMD} --color=always -C 2 {}" --preview-window="up,70%:wrap" --ansi --bind="enter:execute({RG_BASE_CMD} --passthru {} > {}.temp && mv {}.temp {}),shift-tab:up,tab:down" --cycle'
NONINTERACTIVE_CMD = "{RG_BASE_CMD} -l | xargs -I @ sh -c '{RG_BASE_CMD} --passthru @ > @.temp && mv @.temp @' "

# helper functions
def create_rg_base_cmd(parsed_args) -> str:
    out = f"rg {parsed_args.old} {parsed_args.rg_opt}"
    if any(parsed_args.new):
        out = f"{out} -r {parsed_args.new}"
    return out

def trigger(parsed_args) -> None:
    rg_base_cmd = create_rg_base_cmd(parsed_args)
    full_cmd = None
    if parsed_args.interactive:
        full_cmd = INTERACTIVE_CMD.replace("{RG_BASE_CMD}", rg_base_cmd)
    else:
        full_cmd = NONINTERACTIVE_CMD.replace("{RG_BASE_CMD}", rg_base_cmd)
    try:
        subprocess.check_call(full_cmd, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        pass

if __name__ == "__main__":
    cli = ArgumentParser()
    cli.add_argument("-c", "--rg-opt", type=str, help="ripgrep options", dest="rg_opt", required=True)
    cli.add_argument("-o", "--old", type=str, help="pattern to replace", dest="old", required=True)
    cli.add_argument("-n", "--new", type=str, help="replace with", dest="new", required=False, default="")
    cli.add_argument("-i", "--interactive", action="store_true", dest="interactive")
    parsed_args = cli.parse_args()

    trigger(parsed_args)
