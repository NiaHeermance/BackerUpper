import os
import platform
import sys
import json
from pathlib import Path

ARGUMENT_FOR_DEPLOY = "--Deploy"

WINDOWS_PREFACE = "wsl"

SYNC_COMMAND = "rsync -a --delete"

def get_sync_information():
    with open("../Configuration/Files/sync_config.json", "r") as config:
        return json.load(config)


def get_commandline_arguments():
    if len(sys.argv) > 2:
        message = "Error: More than one command line argument provided."
        print(message)
        exit(1)

    arguments = {}
    if len(sys.argv) == 1:
        arguments["Deploy"] = False
    elif sys.argv[1] == ARGUMENT_FOR_DEPLOY:
        arguments["Deploy"] = True
    else:
        message = f"""Error: Provided command line argument is not '{ARGUMENT_FOR_DEPLOY}'.
Given: {sys.argv[1]}
"""
        print(message)
        exit(1)
    return arguments


def path_to_string(path: Path, quoted: bool = True):
    if quoted:
        return f'"{path.as_posix()}/"'
    else:
        return f'{path.as_posix()}/'


def standardize_path_string(path: str):
    return path_to_string(Path(path), False)


def get_source_and_dest_strings(local: Path, backup: Path, to_deploy: bool):
    local_ret = path_to_string(local)
    backup_ret = path_to_string(backup)

    if to_deploy:
        return backup_ret, local_ret
    else:
        return local_ret, backup_ret


def determine_excluded(to_save: list, all_excluded: list):
    dict_excluded = {}
    for save_folder in to_save:
        these_excluded = []
        
        for exclude_folder in all_excluded:
            if exclude_folder.startswith(save_folder):
                these_excluded.append(exclude_folder[len(save_folder):])
        
        if len(these_excluded) > 0:
            dict_excluded[save_folder] = these_excluded

    return dict_excluded


def create_exclude_statement(folders: list):
    folders_formatted = [path_to_string(Path(folder)) for folder in folders]
    folders_to_exclude = " --exclude " + ' --exclude '.join(folders_formatted)
    return folders_to_exclude


def save_or_deploy_all(
        to_deploy: bool,
        backup: Path,
        local: Path,
        local_location: dict
    ):
    source, dest = get_source_and_dest_strings(local, backup, to_deploy)

    command = f'{SYNC_COMMAND} {source} {dest}'

    if not to_deploy and "Exclude" in local_location:
        command += create_exclude_statement(local_location["Exclude"])

    run_linux_command(command)


def save_or_deploy_specific_folders(
        to_deploy: bool,
        backup_twothirds: Path,
        local_start: Path,
        folders_to_save: list,
        excluded: dict
    ):
    for path_ending in folders_to_save:
        local = local_start / path_ending
        backup = backup_twothirds / path_ending
        source, dest = get_source_and_dest_strings(local, backup, to_deploy)

        if not os.path.isdir(dest):
            run_linux_command(f"mkdir -p {dest}")

        command = f'{SYNC_COMMAND} {source} {dest}'

        path_ending_formatted = standardize_path_string(path_ending)
        if not to_deploy and path_ending_formatted in excluded:
            command += create_exclude_statement(excluded[path_ending_formatted])

        run_linux_command(command)


def run_linux_command(command: str):
    if platform.system() == "Windows":
        command = f'{WINDOWS_PREFACE} {command}'
    print(command)
    os.system(command)


def main():
    to_sync = get_sync_information()
    arguments = get_commandline_arguments()
    to_deploy = arguments["Deploy"]

    for backup_type, backup_info in to_sync.items():
        backup_start = Path(backup_info["Backup Folder"])
        local_info = backup_info["Local Folders"]

        for local_location in local_info:
            local_start = Path(local_location["Root"])
            backup_continuation = Path(local_location["Backup Root"])
            backup_twothirds = backup_start / backup_continuation

            folders_to_save = local_location["To Save"]
            if folders_to_save == "All":
                save_or_deploy_all(
                    to_deploy,
                    backup_twothirds,
                    local_start,
                    local_location
                )
            else:
                folders_to_save = [standardize_path_string(folder) for folder in folders_to_save]
                excluded = {}
                if "Exclude" in local_location:
                    excluded = [standardize_path_string(folder) for folder in local_location["Exclude"]]
                    excluded = determine_excluded(folders_to_save, excluded)

                save_or_deploy_specific_folders(
                    to_deploy,
                    backup_twothirds,
                    local_start,
                    folders_to_save,
                    excluded
                )


if __name__ == "__main__":
    main()
