import os
import re

import click
from PyInquirer import prompt
from termcolor import colored

from boom.handlers.package_handler import PackageHandler
from boom.handlers.project_handler import ProjectHandler
from boom.handlers.structure_handler import StructureHandler
from boom.handlers.template_handler import TemplateHandler


@click.command('generate', short_help='Generates a new module in project')
@click.argument('module', required=True, type=click.STRING)
@click.argument('name', required=True, nargs=-1, type=click.STRING)
@click.option('-r', '--project_root', default=os.getcwd(), type=click.Path(exists=True, file_okay=False, writable=True))
@click.option('-v', '--verbose', count=True)
@click.pass_context
def run(ctx, **kwargs):
    click.secho(
        'Welcome to Flask-Boom! This CLI will walk you through generating a module within your project',
        fg='cyan')

    # Set verbose level
    verbose = kwargs.get('verbose', 0)
    if verbose is not None:
        kwargs.pop('verbose')

    # Convert tuple project name to string
    if len(kwargs.get('name')) > 0:
        kwargs.update(name='-'.join(kwargs.get('name')))

    project_handler = ProjectHandler(ctx, verbose=verbose)
    project_handler.load_project(kwargs.get('project_root', os.getcwd()))
    project_handler.generate_module(kwargs.get('module'), kwargs.get('name'))
