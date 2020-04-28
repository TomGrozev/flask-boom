import os
import re

import click
from PyInquirer import prompt
from termcolor import colored

from boom.handlers.project_handler import ProjectHandler
from boom.handlers.template_handler import TemplateHandler

url_pattern = re.compile("^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$")


@click.command('new', short_help='Creates a new project')
@click.argument('project_name', required=False, nargs=-1, type=click.STRING)
@click.option('-a', '--author_name', nargs=2, type=click.STRING)
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
        kwargs.update(project_name=' '.join(kwargs.get('project_name')))
    if len(kwargs.get('author_name')) > 0:
        kwargs.update(author_name=' '.join(kwargs.get('author_name')))

    template_handler = TemplateHandler(ctx, verbose)

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
            'type': 'input',
            'name': 'project_description',
            'message': 'Description of your project (min 20 characters):',
            'validate': lambda val: len(val) >= 20,
            'when': lambda _: kwargs.get('project_description') is None
        },
        {
            'type': 'input',
            'name': 'author_name',
            'message': 'Name of the author:',
            'validate': lambda val: len(val) >= 4,
            'when': lambda _: len(kwargs.get('author_name')) == 0
        },
        {
            'type': 'input',
            'name': 'author_url',
            'message': 'URL to author page (usually a GitHub page):',
            'validate': lambda val: bool(url_pattern.match(val)),
            'when': lambda _: kwargs.get('author_url') is None
        },
        {
            'type': 'list',
            'name': 'template',
            'message': 'Template to use:',
            'choices': template_handler.template_option_names,
            'filter': lambda t: template_handler.templates[template_handler.template_option_names.index(t)]
        }
    ]

    answers = prompt(questions)
    root_vars = {**kwargs, **answers}

    # Add new vars
    root_vars.update(project_name_path=re.sub('[^A-Za-z0-9_ ]+', '',
                                              root_vars.get('project_name').lower().replace(' ', '_')
                                              .replace('-', '_')))

    # Update target path
    if root_vars.get('project_root') is None:
        project_root = os.path.abspath(root_vars.get('project_name_path'))
    else:
        project_root = os.path.join(os.path.abspath(root_vars.get('project_root')),
                                    root_vars.get('project_name_path'))
    root_vars.pop('project_root')

    # Create Handler (also validates structure)
    project_structure = ProjectHandler(ctx, verbose=verbose)
    project_structure.create_project(project_root, root_vars)


def __validate_project_name__(project_name) -> bool:
    pattern = re.compile("^[a-zA-Z][a-zA-Z0-9 ]{2,}$")
    return bool(pattern.match(project_name))
