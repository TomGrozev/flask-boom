import os
import re

import click
from PyInquirer import prompt
from termcolor import colored

from boom.handlers.package_handler import PackageHandler
from boom.handlers.structure_handler import StructureHandler
from boom.handlers.template_handler import TemplateHandler


@click.command('new', short_help='Creates a new project')
@click.argument('project_name', required=False, nargs=-1, type=click.STRING)
@click.option('-d', '--project_description', type=click.STRING)
@click.option('-a', '--author_name', type=click.STRING)
@click.option('-u', '--author_url', type=click.STRING)
@click.option('-r', '--project_root', type=click.Path(file_okay=False, writable=True))
@click.option('-v', '--verbose', count=True)
@click.pass_context
def run(ctx, **kwargs):
    click.secho(
        'Welcome to Flask-Boom! This CLI will walk you through creating the project structure for your flask project',
        fg='cyan')

    # Set verbose level
    verbose = kwargs.get('verbose', 0)
    if verbose is not None:
        kwargs.pop('verbose')

    # Convert tuple project name to string
    if len(kwargs.get('project_name')) > 0:
        kwargs.update(project_name='-'.join(kwargs.get('project_name')))

    template_handler = TemplateHandler(ctx)

    if len(template_handler.templates) == 0:
        click.secho('No valid templates available for use', fg='red', bold=True)
        ctx.abort()

    try:
        import pip
    except ImportError:
        ctx.fail(colored('Pip is not installed. Pip is required to install packages using the boom CLI'))

    try:
        import venv
    except ImportError:
        ctx.fail(colored('Venv is not installed. Venv is required to install packages using the boom CLI'))

    questions = [
        {
            'type': 'input',
            'name': 'project_name',
            'message': 'What\'s the name of your project?',
            'validate': __validate_project_name__,
            'when': lambda _: len(kwargs.get('project_name')) == 0
        },
        {
            'type': 'editor',
            'name': 'project_description',
            'message': 'Description of your project:',
            'eargs': {'editor': 'vi'},
            'when': lambda _: kwargs.get('project_description') is None
        },
        {
            'type': 'input',
            'name': 'author_name',
            'message': 'Name of the author:',
            'when': lambda _: kwargs.get('author_name') is None
        },
        {
            'type': 'input',
            'name': 'author_url',
            'message': 'URL to author page (usually a GitHub page):',
            'when': lambda _: kwargs.get('author_url') is None
        },
        {
            'type': 'list',
            'name': 'template',
            'message': 'Template to use:',
            'basic': 'Default',
            'choices': template_handler.template_option_names,
            'filter': lambda t: template_handler.templates[template_handler.template_option_names.index(t)]
        }
    ]

    answers = prompt(questions)
    root_vars = {**kwargs, **answers}

    # Add new vars
    root_vars.update(project_name_path=root_vars.get('project_name').lower().replace(' ', '-'))

    # Update target path
    if root_vars.get('project_root') is None:
        root_vars.update(project_root=os.path.abspath(root_vars.get('project_name_path')))
    else:
        root_vars.update(project_root=os.path.join(os.path.abspath(root_vars.get('project_root')),
                                                   root_vars.get('project_name_path')))

    # Create Handler (also validates structure)
    structure_handler = StructureHandler(ctx, root_vars, verbose)

    # Select template
    template_handler.select_template(root_vars.get('template', {}))

    # Create project structure (including files)
    structure_handler.create_project_structure()

    # Create virtual environment
    PackageHandler(ctx, root_vars.get('project_root'), verbose).start_venv()


def __validate_project_name__(project_name) -> bool:
    pattern = re.compile("^[a-zA-Z][a-zA-Z0-9 ]{2,}$")
    return bool(pattern.match(project_name))
