# Vendor imports
import click

# Internal imports
import cli.check_version

@click.group()
def root():
    """CI command line helper for epx-results"""
    pass

@click.command("check_version")
def check_version_command():
    check_version.execute()

def execute():
    root.add_command(check_version_command)
    root()
