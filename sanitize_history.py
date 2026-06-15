import os
import subprocess
import sys

REPLACEMENT_TEXT = "--- REMOVED SECRET ---"

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing {' '.join(cmd)}:\n{e.stderr}")
        sys.exit(1)

def main():
    workspace_dir = os.environ.get("WORKSPACE_DIR", os.getcwd())
    target_secret = os.environ.get("TARGET_SECRET", "")

    if not target_secret:
        print("Error: TARGET_SECRET environment variable is empty. Nothing to sanitize.")
        sys.exit(1)

    dict_file_path = os.path.abspath(os.path.join(workspace_dir, "dict.txt"))

    with open(dict_file_path, "w", encoding="utf-8") as f:
        f.write(f"literal:{target_secret}==>{REPLACEMENT_TEXT}\n")

    print("Running git-filter-repo to purge secrets from history...")
    run_command(
        ["git-filter-repo", "--replace-text", dict_file_path, "--force"],
        cwd=workspace_dir,
    )

    os.remove(dict_file_path)
    print("History rewriting complete.")

if __name__ == "__main__":
    main()
