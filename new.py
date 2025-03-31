import subprocess
import difflib
from pathlib import Path
import getpass
from typing import List, Tuple


class ConfigComparator:
    COLOR_RESET = '\033[0m'
    COLOR_GREEN = '\033[92m'
    COLOR_RED = '\033[91m'

    def __init__(self, target_hosts_file: str):
        self.target_hosts_file = Path(target_hosts_file)

    def load_targets(self) -> List[Tuple[str, Path]]:
        targets = []
        with self.target_hosts_file.open() as f:
            for line in f:
                if line.strip():
                    hostname, local_config_path = line.strip().split()
                    targets.append((hostname, Path(local_config_path)))
        return targets

    def fetch_remote_config(self, hostname: str, password: str) -> str:
        commands = f'enable\n{password}\nterminal length 0\nshow run\nexit\n'
        result = subprocess.run(
            ['ssh', '-tt', hostname],
            input=commands,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise ConnectionError(f"Error connecting to {hostname}: {result.stderr.strip()}")

        return result.stdout.replace('\r\n', '\n').strip()

    def save_config(self, config: str, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(config)

    def compare_configs(self, hostname: str, remote_config: str, local_config_path: Path):
        if not local_config_path.exists():
            print(f"Local config for {hostname} not found. Saving remote config.")
            self.save_config(remote_config, local_config_path)
            return

        local_config = local_config_path.read_text().replace('\r\n', '\n').strip()
        diff = difflib.unified_diff(
            local_config.splitlines(keepends=True),
            remote_config.splitlines(keepends=True),
            fromfile=f'local/{hostname}.cfg',
            tofile=f'remote/{hostname}.cfg'
        )

        diff_output = ''.join(diff)
        if diff_output:
            print(f"Differences found for {hostname}:")
            self.display_diff(diff_output)
        else:
            print(f"No differences for {hostname}.")

    def display_diff(self, diff_output: str):
        for line in diff_output.splitlines():
            color = self.COLOR_RESET
            if line.startswith('+'):
                color = self.COLOR_GREEN
            elif line.startswith('-'):
                color = self.COLOR_RED

            print(f"{color}{line}{self