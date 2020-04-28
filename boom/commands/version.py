import platform
import sys
import click
import boom

from pip._internal.operations import freeze
from tabulate import tabulate


@click.command('version', short_help='Gets version information of boom')
def run():
    click.echo('\n')
    click.echo('Flask Boom: %s' % boom.__version__)
    click.echo('Python: %d.%d.%d' % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    click.echo('OS: %s %s' % (platform.system(), platform.release()))
    click.echo('\n')

    # Package Versions
    click.secho('Installed Packages\n', fg='cyan', bold=True)
    package_freeze = freeze.freeze()
    rows = [package.split('==', maxsplit=1) for package in package_freeze]
    click.echo(tabulate(rows, headers=['Package', 'Version']))