import os
import subprocess
import sys
import shutil

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing {' '.join(cmd)}:\n{e.stderr}")
        sys.exit(1)

def main():
    # In CI, we run directly inside the already-cloned workspace repository
    workspace_dir = os.getcwd()
    
    # Grab secrets mapped from GitHub Action environment variables
    # Expected format in env: SECRET_MAP = "secret1==REDACTED_1|secret2==REDACTED_2"
    secret_map_raw = os.environ.get("SECRET_MAP", "")
    
    if not secret_map_raw:
        print("Error: SECRET_MAP environment variable is empty. Nothing to sanitize.")
        sys.exit(1)
        
    replacements = []
    for pair in secret_map_raw.split("|"):
        if "==" in pair:
            replacements.append(pair.split("==", 1))

    # Create the filter-repo expressions file
    dict_file_path = os.path.abspath(os.path.join(workspace_dir, "dict.txt"))
    with open(dict_file_path, "w") as f:
        for secret, replacement in replacements:
            f.write(f"literal:{secret}==>{replacement}\n")

    print("Running git-filter-repo to purge secrets from history...")
    
    # Run filter-repo directly on the current workspace
    run_command([
        "git-filter-repo", 
        "--replace-text", dict_file_path,
        "--force"
    ], cwd=workspace_dir)

    if os.path.exists(dict_file_path):
        os.remove(dict_file_path)

    print("History rewriting complete locally.")

if __name__ == "__main__":
    main()