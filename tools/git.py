import subprocess

# * This script is used to commit changes to a git repository.
message = "update"


commands = [["git", "add", "."], ["git", "commit", "-m", message], ["git", "pull", "origin", "main", "--rebase"], ["git", "push", "origin", "main"]]
for cmd in commands:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error executing: {' '.join(cmd)}")
        print(result.stderr)
    print(result.stdout.strip())
