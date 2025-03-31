import subprocess
import difflib
from pathlib import Path
import getpass

TARGET_HOSTS_FILE = './target_hosts.txt'

COLOR_RESET = '\033[0m'
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'


def load_targets(file_path):
    with open(file_path) as f:
        return [line.strip().split() for line in f if line.strip()]


def fetch_config(hostname, password):
    commands = f'enable\n{password}\nterminal length 0\nshow run\nexit\n'
    result = subprocess.run(['ssh', '-tt', hostname], input=commands, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error connecting to {hostname}: {result.stderr}")
        return None
    return result.stdout.replace('\r\n', '\n').strip()


def compare_configs(hostname, remote_config, local_config_path):
    local_path = Path(local_config_path)
    if not local_path.exists():
        print(f"Local config for {hostname} not found. Saving remote config.")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        local_path.write_text(remote_config)
        return

    local_config = local_path.read_text().replace('\r\n', '\n').strip()
    diff = difflib.unified_diff(
        local_config.splitlines(keepends=True),
        remote_config.splitlines(keepends=True),
        fromfile=f'local/{hostname}.cfg',
        tofile=f'remote/{hostname}.cfg'
    )

    diff_output = ''.join(diff)
    if diff_output:
        print(f"Differences found for {hostname}:")
        for line in diff_output.splitlines():
            color = COLOR_GREEN if line.startswith('+') else COLOR_RED if line.startswith('-') else COLOR_RESET
            print(f"{color}{line}{COLOR_RESET}")
    else:
        print(f"No differences for {hostname}.")


def main():
    targets = load_targets(TARGET_HOSTS_FILE)
    password = getpass.getpass("Enter enable password: ")

    for hostname, local_config_path in targets:
        print(f"Checking host: {hostname}")
        remote_config = fetch_config(hostname, password)
        if remote_config:
            compare_configs(hostname, remote_config, local_config_path)


if __name__ == "__main__":
    main()
