"""
CLI entry point.
"""

import click

from .commands.download import download
from .commands.geo import geo
from .commands.setup import setup
from .commands.tax import tax


@click.group()
def main():
    pass


main.add_command(download)
main.add_command(geo)
main.add_command(setup)
main.add_command(tax)
