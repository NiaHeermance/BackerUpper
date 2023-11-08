import os
import json

def main():
    to_store = {}
    with open("../Configuration/Files/sync_config.json", "r") as configuration:
        to_store = json.load(configuration)

    command_start = "wsl rsync -a --delete"

    for backup_type, backup_info in to_store.items():
        backup_path_start = backup_info["Backup Folder"]
        if backup_path_start[-1] != '/':
            backup_path_start += '/'

        local_info = backup_info["Local Folders"]
        for local_location in local_info:
            local_path_start = local_location["Root"]
            if local_path_start[-1] != '/':
                local_path_start += '/'

            backup_path_continuation = local_location["Backup Root"]
            if backup_path_continuation[-1] != '/':
                backup_path_continuation += '/'
            backup_path_specific_start = backup_path_start + backup_path_continuation

            folders_to_save = local_location["To Save"]
            if folders_to_save == "All":
                source_path = f"\"{local_path_start}\""
                dest_path = f"\"{backup_path_specific_start}\""
                command = f'{command_start} {source_path} {dest_path}'

                if "Exclude" in local_location:
                    folders_to_exclude = f"\"{"\" \"".join(local_location["Exclude"])}\""
                    command += f" --exclude {folders_to_exclude}"

                print(command)
                os.system(command)

            else:
                for to_save_fold in folders_to_save:
                    source_path = f"\"{local_path_start}{to_save_fold}\""
                    dest_path = f"\"{backup_path_specific_start}{to_save_fold}"

                    last_slash = dest_path.rindex("/")
                    dest_path = dest_path[0:last_slash] + "\""

                    if not os.path.isdir(dest_path):
                        os.system(f"wsl mkdir -p {dest_path}")

                    command = f'{command_start} {source_path} {dest_path}'
                    print(command)
                    os.system(command)


if __name__ == "__main__":
    main()