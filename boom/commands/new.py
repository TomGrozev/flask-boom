import os
import re
import shutil

import click
from PyInquirer import prompt
from termcolor import colored
from jinja2 import Template

from boom.utils.path_helper import is_path_creatable, is_pathname_valid


@click.command('new', short_help='Creates a new project')
@click.argument('project_name', required=False, nargs=-1, type=click.STRING)
@click.option('-t', '--target', type=click.Path(file_okay=False, writable=True))
@click.option('-v', '--verbose', count=True)
@click.pass_context
def run(ctx, **kwargs):
    click.secho(
        'Welcome to Flask-Boom! This CLI will walk you through creating the project structure for your flask project',
        fg='cyan')

    print(kwargs)
    verbose = kwargs.get('verbose', None)
    if verbose is not None:
        kwargs.pop('verbose')

    if kwargs.get('project_name') is not None:
        kwargs.update(project_name=' '.join(kwargs.get('project_name')))

    questions = [
        {
            'type': 'input',
            'name': 'project_name',
            'message': 'What\'s the name of your project?',
            'validate': __validate_project_name__,
            'when': lambda _: kwargs.get('project_name') is None
        },
        {
            'type': 'input',
            'name': 'project_description',
            'message': 'Short description of your project:'
        },
        {
            'type': 'list',
            'name': 'template',
            'message': 'Template to use:',
            'default': 'Default',
            'choices': [t.capitalize() for t in os.listdir(ctx.obj['TEMPLATES_FOLDER'])],
            'filter': lambda t: t.lower()
        }
    ]

    answers = prompt(questions)

    result = {**kwargs, **answers}

    project_name_path = result.get('project_name').lower().replace(' ', '-')
    result.update(project_name_path=project_name_path)

    if result.get('target') is None:
        result.update(target=project_name_path)
    else:
        result.update(target=result.get('target') + '/' + project_name_path)

    print(result)

    # Valid target
    if not __validate_target_path__(result.get('target')):
        return click.secho('Target path is invalid. Could be a permissions error.', err=True, fg='red', bold=True)

    # Directory is not empty
    if len(os.listdir(result.get('target'))) > 0:
        click.confirm(colored('The target directory is not empty, continuing with overwrite files. Do you want to '
                              'continue?', 'red', attrs=['bold']), abort=True, err=True)
        # Clear directory
        if verbose >= 1:
            click.secho('Emptying target directory', fg='yellow')
        for filename in os.listdir(result.get('target')):
            file_path = os.path.join(result.get('target'), filename)
            if verbose >= 2:
                click.secho('Attempting to delete %s' % file_path, fg='yellow')
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                if verbose >= 1:
                    click.secho('Failed to %s. Reason: %s' % (file_path, e), fg='yellow')
                ctx.fail('Failed to clear contents of target directory')

    # Create target if does not exist
    if not os.path.exists(result.get('target')):
        if verbose >= 1:
            click.secho('Target directory does not exist, creating.', fg='yellow')
        os.makedirs(result.get('target'))

    template = ctx.obj['TEMPLATES_FOLDER'] + '/' + result.get('template')
    __create_files_for_dir__(template, result.get('target'), result)


def __validate_project_name__(project_name) -> bool:
    pattern = re.compile("^[a-zA-Z ]*$")
    return bool(pattern.match(project_name))


def __validate_target_path__(target_path, verbose=None) -> bool:
    if not is_pathname_valid(target_path) and verbose >= 1:
        click.secho('Target is not a valid pathname.', fg='yellow')
        return False
    if not is_path_creatable(target_path):
        if not os.path.exists(target_path):
            click.secho('Target does not exist and is not creatable.', fg='yellow')
            return False
        if not os.path.isdir(target_path):
            click.secho('Target is not a directory and is not creatable.', fg='yellow')
            return False
    return True


def __create_files_for_dir__(template_dir, out_dir, template_vars):
    for filename in os.listdir(template_dir):
        file_path = template_dir + '/' + filename
        t_file_path = out_dir + '/' + filename
        if os.path.isdir(file_path):
            os.makedirs(t_file_path)
            __create_files_for_dir__(file_path, t_file_path, template_vars)
            continue
        f = open(file_path, 'r')
        tm = Template(f.read())
        r = tm.render(**template_vars)
        out = open(t_file_path, 'w+')
        out.write(r)
        out.close()
