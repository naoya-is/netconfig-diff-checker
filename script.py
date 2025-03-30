import subprocess
import difflib
import os
from pathlib import Path

TARGET_HOSTS_FILE = './target_hosts.txt'

# ANSIカラーコード
COLOR_RESET = '\033[0m'
COLOR_GREEN = '\033[92m'
COLOR_RED = '\033[91m'

# 指定したファイルからホスト名とコンフィグパスを取得する
def get_target_hosts_configs(file_path):
    hosts_configs = []
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                hosts_configs.append((parts[0], parts[1]))
    return hosts_configs

# ネイティブのsshコマンドを使ってshow runを取得する
def fetch_remote_config(hostname):
    try:
        result = subprocess.run(
            ['ssh', hostname, 'show run'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to {hostname}: {e.stderr}")
        return None

# ローカルファイルと比較する
def compare_config(hostname, remote_config, local_config_path):
    local_config_path = Path(local_config_path)

    if not local_config_path.exists():
        print(f"Local config for {hostname} not found, saving remote config as baseline.")
        local_config_path.parent.mkdir(parents=True, exist_ok=True)
        local_config_path.write_text(remote_config)
        return

    local_config = local_config_path.read_text()

    diff = difflib.unified_diff(
        local_config.splitlines(keepends=True),
        remote_config.splitlines(keepends=True),
        fromfile=f'local/{hostname}.cfg',
        tofile=f'remote/{hostname}.cfg'
    )

    diff_output = ''.join(diff)

    if diff_output:
        print(f"Difference found for {hostname}:")
        for line in diff_output.splitlines():
            if line.startswith('+'):
                print(f"{COLOR_GREEN}{line}{COLOR_RESET}")
            elif line.startswith('-'):
                print(f"{COLOR_RED}{line}{COLOR_RESET}")
            else:
                print(line)
    else:
        print(f"No differences for {hostname}.")

# メイン処理
def main():
    hosts_configs = get_target_hosts_configs(TARGET_HOSTS_FILE)

    for hostname, local_config_path in hosts_configs:
        print(f"Processing host: {hostname}")
        remote_config = fetch_remote_config(hostname)
        if remote_config:
            compare_config(hostname, remote_config, local_config_path)

if __name__ == "__main__":
    main()
