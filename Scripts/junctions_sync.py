# _,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'
#
# junctions_sync.py
#
# Running this script will use ../Configuration/Files/junctions.json to create
# the desired directory junctions.
#
# _,.-'~'-.,__,.-'~'-.,__,.-'~'-.,__,.-'~'

import os
import json
from pathlib import Path
import shutil
import filecmp
import sys

INITIAL_HIDDEN_CHAIN_STEM = Path("../.HiddenChains")

def loadJunctionsConfig():
    with open("../Configuration/Files/junctions.json", "r") as configuration_file:
        config = json.load(configuration_file)
        return config["Junctions"]


def processTargetEnd(linkname: Path, target_twothirds: Path, target_end: str):
    star_count = target_end.count("*")
    if star_count > 2:
        print("Error: Too many * in ", target_end)
        exit(1)
    elif star_count == 1:
        star = target_end.index("*")
        linkname_final_layer = linkname.parts[-1]
        target_end = "".join([target_end[:star], linkname_final_layer, target_end[star+1:]])

    return target_twothirds / target_end


def isEachEmptyExceptNextLayer(starting_layer: Path, end_layer: str):
    path = starting_layer
    for layer in Path(end_layer).parts[:-1]:
        path = path / layer
        if not path.exists():
            return True
        if len(path.listdir) > 1:
            return False
    return True


def createHiddenChain(linkname_start: Path, linkname_end: str, final_target: Path):
    if not isEachEmptyExceptNextLayer(linkname_start, linkname_end):
        print(
            "Error: Tried to use Hidden Chain with a non-empty in chain.\n",
            f"Chain was {linkname_end}"
        )
        exit(1)
    try:
        slash = linkname_end.rindex("/")
    except:
        print(
            "Error: Tried to use Hidden Chain with only one directory in chain.\n",
            f"Chain was {linkname_end}"
        )
        exit(1)

    linkname = linkname_start / linkname_end
    if linkname.exists():
        moveFiles(linkname, final_target)
    first_part = Path(linkname_end).parts[0]
    first_layer = linkname_start / first_part
    if first_layer.exists():
        shutil.rmtree(first_layer)

    linkname_end_minus_finale = linkname_end[:slash]
    second_to_last_target = INITIAL_HIDDEN_CHAIN_STEM / linkname_end_minus_finale
    makeDir(second_to_last_target)

    junctionCommand(first_layer, INITIAL_HIDDEN_CHAIN_STEM / first_part)
    return Path.cwd() / INITIAL_HIDDEN_CHAIN_STEM / linkname_end



def createJunction(linkname_start: Path, linkname_end: str, target_twothirds: Path, target_info: dict):
    linkname = linkname_start / linkname_end
    if isJunction(linkname): # is_junction stopped working for some reason.
        # print("Junction from ", linkname, " already exists.")
        return
    has_hidden_chain = "Hidden Chain" in target_info and target_info["Hidden Chain"]
    first_layer = linkname_start / Path(linkname_end).parts[0]
    if has_hidden_chain and isJunction(first_layer):
        # print("Junction from ", linkname, " already exists.")
        return

    if "Out" in target_info:
        target = processTargetEnd(linkname, target_twothirds, target_info["Out"])
    else:
        target = target_twothirds
    makeDir(target)

    if has_hidden_chain:
        linkname = createHiddenChain(linkname_start, linkname_end, target)
    elif linkname.exists():
        moveFiles(linkname, target)
        shutil.rmtree(linkname)

    junctionCommand(linkname, target)


def isJunction(linkname: Path) -> bool:
    try:
        return bool(os.readlink(linkname))
    except OSError:
        return False


def moveFiles(source: Path, destination: Path):
    files = source.iterdir()
    for file in files:
        try:
            shutil.move(file, destination)
        except:
            potential_duplicate = destination / file.name
            if not filecmp.cmp(file, potential_duplicate):
                new_name =  destination / (file.stem + f' (From Prior Dir){file.suffix}')
                file.replace(new_name)


def makeDir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def junctionCommand(linkname, target):
    os.system(f'mklink /J "{str(linkname)}" "{str(target)}"')


def main():
    junctions = loadJunctionsConfig()

    for junction_starts in junctions:
        linkname_start = Path(junction_starts["LinkName Start"])
        targets = junction_starts["Targets"]
        for target_area in targets:
            target_mid = target_area["Target Continuation"]
            target_twothirds = linkname_start / target_mid
            target_infos = target_area["Directories"]
            for linkname_end, target_info in target_infos.items():
                createJunction(linkname_start, linkname_end, target_twothirds, target_info)


if __name__ == "__main__":
    main()