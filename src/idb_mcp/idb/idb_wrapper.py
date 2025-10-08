import os
import subprocess

from .idb_error import IDBError


class IDBWrapper:
    def __init__(self) -> None:
        self.idb_path = os.environ.get("ASKUI_IDB_PATH", "idb")

    def run_command(self, args: list[str]) -> str:
        try:
            result = subprocess.run(
                [self.idb_path] + args,
                stdout=subprocess.PIPE,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except FileNotFoundError as e:
            raise IDBError(
                f"IDB binary not found at: {self.idb_path}. Please make sure fb-idb is installed."
            ) from e
        except subprocess.CalledProcessError as e:
            raise IDBError(
                f"IDB command failed: {' '.join([self.idb_path] + args)}\n"
                f"Exit code: {e.returncode}\n"
                f"Error output: {e.stderr.strip()}"
            ) from e
