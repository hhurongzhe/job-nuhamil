import os
import glob


def clean_files():
    """
    Deletes files in the current directory with specific prefixes.
    """
    prefixes = ["./script/*", "./result/*"]
    prefixes.append("./workspace/*")
    prefixes.append("./workspace/cfp/*")
    prefixes.append("./workspace/ops/*")
    files_to_delete = []

    # Find all files with the specified prefixes
    for prefix in prefixes:
        files_to_delete.extend(glob.glob(f"{prefix}*"))

    if not files_to_delete:
        print("No files to delete found.")
        return

    # Print the list of files to be deleted for confirmation
    print("The following files will be deleted:")
    for file_name in files_to_delete:
        print(f"  - {file_name}")

    # Ask for confirmation before proceeding
    confirm = input("\nAre you sure you want to proceed? (y/n): ")
    if confirm.lower() == "y":
        for file_name in files_to_delete:
            try:
                os.remove(file_name)
                print(f"Deleted: {file_name}")
            except OSError as e:
                print(f"Error deleting {file_name}: {e}")
        print("\nCleanup complete.")
    else:
        print("Cleanup aborted.")


if __name__ == "__main__":
    clean_files()
