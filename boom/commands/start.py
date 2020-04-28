import os

import click


@click.command('start', short_help='Starts Flask Dev Server')
@click.argument('FILE', required=False)
def run(**kwargs):
    if kwargs.get('file', None) is not None:
        start_file_name: str = kwargs.get('file', None)
        if not start_file_name.endswith('.py'):
            start_file_name += '.py'
    else:
        # Possible start files
        start_files = ['app.py', 'application.py', 'server.py', 'flask.py']

        dir_files = os.listdir()

        # Try find application file
        found_start_files = list(set(start_files).intersection(dir_files))
        if len(found_start_files) == 0:
            click.secho('Could not find flask start file. Try specifying it.')
            return

        start_file_name = found_start_files[0]

    os.environ['FLASK_ENV'] = 'development'
    os.system('python ' + start_file_name)
