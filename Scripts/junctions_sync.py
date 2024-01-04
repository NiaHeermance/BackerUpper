import os
import subprocess
import json
from pathlib import Path
import shutil

INITIAL_HIDDEN_CHAIN_STEM = "../hidden_chains/"

def loadJunctionsConfig():
    with open("../Configuration/Files/junctions.json", "r") as configuration:
	    return configuration["Junctions"]


def process_target_end(linkname, target_start, target_end):
    star_count = target_end.count("*"):
    if star_count > 2:
        print("Error: Too many * in ", target_end)
        exit(1)
    elif star_count == 1:
        star = target_end.index("*")
        slash = linkname.rindex("/")
        linkname_final_dir = linkname[slash+1:]
        target_end = target_end[:star] + linkname_final_dir + target_end[star+1:]

    return target_start + target_end


def create_hidden_chain(linkname, linkname_end):
    try:
        slash = linkname_end.rindex("/")
    except:
        print("Error: Tried to use Hidden Chain with only one directory in chain.\n",
            f"Chain was {linkname_end}"
        )
        exit(1)
    linkname_end = linkname_end[:slash]
    target = INITIAL_HIDDEN_CHAIN_STEM + linkname_end
    make_dir(target)

    linkname_end_purepath = Path(linkname_end)
    first_part = linkname_end_purepath.parts[0]
    junction_command(linkname + first_part, INITIAL_HIDDEN_CHAIN_STEM + first_part)
    return target



def create_junction(linkname, linkname_end, target_start, target):
    if os.path.isjunction(linkname):
        # print("Junction from ", linkname, " already exists.")
        return

    if "Out" in target:
        target = process_target_end(linkname, target_start, target["Out"])
    else:
        target = target_start
    make_dir(target)

    if "Hidden Chain" in target and target["Hidden Chain"]:
        linkname = create_hidden_chain(linkname, linkname_end)

    link_path = Path(linkname)
    if link_path.exists():
        shutil.move(linkname, target)
        shutil.rmtree(linkname)

    junction_command(linkname, target)


def make_dir(path_string):
    path = Path(path_string)
    path.mkdir(parents=True, exist_ok=True)


def junction_command(linkname, target):
    os.system(f'mklink /J "{linkname}" "{target}"')


def main():
    junctions = loadJunctionsConfig()

    for junction_starts in junctions:
        linkname_start = junction_starts["LinkName Start"]
        targets = junction_starts["Targets"]
        for target_area in targets:
            target_start = target_area["Target Start"]
            target_start = f'{linkname_start}/{target_mid}'
            targets = target_area["Directories"]
            for linkname_end, target in targets:
                linkname = f'{linkname_start}/{linkname_end}'
                create_junction(linkname, linkname_end, target_start, target)


if __name__ == "__main__":
    main()