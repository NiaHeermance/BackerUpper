import os
import subprocess
import json
from pathlib import Path
import shutil
import filecmp

INITIAL_HIDDEN_CHAIN_STEM = "../.HiddenChains/"

def loadJunctionsConfig():
    with open("../Configuration/Files/junctions.json", "r") as configuration_file:
        config = json.load(configuration_file)
        return config["Junctions"]


def process_target_end(linkname, target_start, target_end):
    star_count = target_end.count("*")
    if star_count > 2:
        print("Error: Too many * in ", target_end)
        exit(1)
    elif star_count == 1:
        star = target_end.index("*")
        slash = linkname.rindex("/")
        linkname_final_dir = linkname[slash+1:]
        target_end = target_end[:star] + linkname_final_dir + target_end[star+1:]

    return f'{target_start}/{target_end}'


def check_if_each_empty_except_next_layer(starting_layer, end_layer):
    path = starting_layer
    for layer in Path(end_layer).parts[:-1]:
        path += "/" + layer
        if len(os.listdir(path)) > 1:
            return False
    return True


def create_hidden_chain(linkname_start, linkname_end, final_target):
    if not check_if_each_empty_except_next_layer(linkname_start, linkname_end):
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

    move_files(f'{linkname_start}/{linkname_end}', final_target)
    first_part = Path(linkname_end).parts[0]
    first_layer = f'{linkname_start}/{first_part}'
    shutil.rmtree(first_layer)

    linkname_end_minus_finale = linkname_end[:slash]
    second_to_last_target = INITIAL_HIDDEN_CHAIN_STEM + linkname_end_minus_finale
    make_dir(second_to_last_target)

    junction_command(first_layer, INITIAL_HIDDEN_CHAIN_STEM + first_part)
    return os.getcwd() + "/" + INITIAL_HIDDEN_CHAIN_STEM + linkname_end



def create_junction(linkname_start, linkname_end, target_start, target_info):
    linkname = f'{linkname_start}/{linkname_end}'
    if os.path.isjunction(linkname):
        # print("Junction from ", linkname, " already exists.")
        return
    has_hidden_chain = "Hidden Chain" in target_info and target_info["Hidden Chain"]
    first_layer = linkname_start + "/" + Path(linkname_end).parts[0]
    if has_hidden_chain and os.path.isjunction(first_layer):
        # print("Junction from ", linkname, " already exists.")
        return


    if "Out" in target_info:
        target = process_target_end(linkname, target_start, target_info["Out"])
    else:
        target = target_start
    make_dir(target)

    link_path = Path(linkname)
    if has_hidden_chain:
        linkname = create_hidden_chain(linkname_start, linkname_end, target)
        print(linkname)
    elif link_path.exists():
        move_files(linkname, target)
        shutil.rmtree(linkname)

    junction_command(linkname, target)


def move_files(source, destination):
    files = os.listdir(source)
    for file in files:
        file_path = source + "/" + file
        try:
            shutil.move(file_path, destination)
        except:
            potential_duplicate = destination + "/" + file
            if not filecmp.cmp(file_path, potential_duplicate):
                file_object = Path(file_path)
                new_name = f'{source}/{file_object.stem} (From Prior Dir){file_object.suffix}'
                os.rename(file_path, new_name)
                shutil.move(new_name, destination)




def make_dir(path_string):
    path = Path(path_string)
    path.mkdir(parents=True, exist_ok=True)


def junction_command(linkname, target):
    linkname = forwardToBackSlash(linkname)
    target = forwardToBackSlash(target)
    os.system(f'mklink /J "{linkname}" "{target}"')


def forwardToBackSlash(str):
    return str.replace("/", "\\")


def main():
    junctions = loadJunctionsConfig()

    for junction_starts in junctions:
        linkname_start = junction_starts["LinkName Start"]
        targets = junction_starts["Targets"]
        for target_area in targets:
            target_start = target_area["Target Start"]
            target_start = f'{linkname_start}/{target_start}'
            targets = target_area["Directories"]
            for linkname_end, target in targets.items():
                create_junction(linkname_start, linkname_end, target_start, target)


if __name__ == "__main__":
    main()