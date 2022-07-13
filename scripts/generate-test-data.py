from pathlib import Path
import click
import json
import os
import subprocess

PKG_DIRECTORY = Path(os.path.abspath(__file__)).parent.parent


class cd:
    """
    Context manager for changing the current working directory
    """

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


@click.group()
@click.version_option()
def root():
    """CLI testing tool for epx-results"""
    pass


@click.command("run")
@click.option(
    "-c", "--config", default="generate-data-config.json", help="configuration file"
)
def run_command(config: str):
    """Runs regression testing for FRED"""
    json_obj = None
    with open(config, encoding="utf-8") as f:
        json_obj = json.loads(f.read())

    for job in json_obj["jobs"]:
        entrypoint = Path(f"{PKG_DIRECTORY}/tests/models/{job['entrypoint']}")
        home_dir = entrypoint.parent
        entry_file = entrypoint.name

        delete_args = ["fred_delete", "-f", "-k", job["key"]]
        subprocess.run(delete_args, capture_output=True)

        args = [
            "fred_job",
            "-p",
            entry_file,
            "-n",
            str(job["runs"]),
            "-m",
            str(json_obj["cores"]),
            "-k",
            str(job["key"]),
        ]
        with cd(home_dir):
            p = subprocess.run(args, capture_output=True)
            print(p)


def main():
    root.add_command(run_command)
    root()


if __name__ == "__main__":
    main()
