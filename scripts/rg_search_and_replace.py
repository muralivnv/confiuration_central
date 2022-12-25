#!/usr/bin/python3

# imports
import subprocess
from argparse import ArgumentParser
import sys

def create_rg_base_cmd(parsed_args) -> str:
    out = f"rg {parsed_args.old} {parsed_args.rg_opt}"
    if any(parsed_args.new):
        out = f"{out} -r {parsed_args.new}"
    return out

def trigger(parsed_args) -> None:
    rg_cmd_base = create_rg_base_cmd(parsed_args)
    full_cmd = f"{rg_cmd_base}"
    if not parsed_args.dry:
        full_cmd = f"{rg_cmd_base} -l | xargs -I @ sh -c '{rg_cmd_base} --passthru @ > @.temp && mv @.temp @' "
    subprocess.check_call(full_cmd, shell=True, stdout=sys.stdout, stderr=subprocess.STDOUT)

if __name__ == "__main__":
    cli = ArgumentParser()
    cli.add_argument("-c", "--rg-opt", type=str, help="ripgrep options", dest="rg_opt", required=True)
    cli.add_argument("-o", "--old", type=str, help="pattern to replace", dest="old", required=True)
    cli.add_argument("-n", "--new", type=str, help="replace with", dest="new", required=False, default="")
    cli.add_argument("-d", "--dry", help="do dry run", dest="dry", action="store_true")
    parsed_args = cli.parse_args()

    trigger(parsed_args)
