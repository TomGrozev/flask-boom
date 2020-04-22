import os
import subprocess
import sys

import click
from termcolor import colored

from boom.utils.path_helper import valid_directory


class PackageHandler:
    __ctx__ = None
    project_root = None
    verbose = 0

    def __init__(self, ctx, project_root, verbose=0) -> None:
        self.__ctx__ = ctx
        self.project_root = project_root
        self.verbose = verbose

        if not valid_directory(project_root):
            ctx.fail(colored('Invalid project directory when setting up packages', 'red', attrs=['bold']))

    def start_venv(self):
        self.create_venv()
        self.install_packages()
        self.update_requirements_versions()

    def create_venv(self):
        click.secho('########### Creating Virtual Environment ###########', fg='cyan')

        try:
            subprocess.check_call([sys.executable, '-m', 'venv', '', os.path.join(self.project_root, 'venv')])
            click.secho('Virtual Environment Created Successfully in venv', fg='green')
        except subprocess.CalledProcessError as e:
            if self.verbose >= 2:
                click.secho(e.__str__(), fg='yellow')
            self.__ctx__.fail(colored('Failed to create virtualenv.', 'red', attrs=['bold']))

    def install_packages(self):
        if not os.path.exists(os.path.join(self.project_root, 'requirements.txt')):
            click.secho('No Requirements to install', fg='cyan')
        req = open(os.path.join(self.project_root, 'requirements.txt'), "r").read()
        if len(req) == 0:
            click.secho('No Requirements to install', fg='cyan')

        click.secho('########### Installing Requirements ###########', fg='cyan')
        try:
            subprocess.check_call(
                [os.path.join(self.project_root, 'venv', 'bin', 'python'), '-m', 'pip', 'install', '-r',
                 os.path.join(self.project_root, 'requirements.txt')])
        except subprocess.CalledProcessError as e:
            if self.verbose >= 2:
                click.secho(e.__str__(), fg='yellow')
            self.__ctx__.fail(colored('Failed to install requirements.', 'red', attrs=['bold']))

    def update_requirements_versions(self):
        click.secho('########### Updating Requirements File ###########', fg='cyan')
        if not os.path.exists(os.path.join(self.project_root, 'requirements.txt')):
            click.secho('Requirements file does not exist', fg='cyan')
        try:
            req_file = open(os.path.join(self.project_root, 'requirements.txt'), "w")
            subprocess.check_call([os.path.join(self.project_root, 'venv', 'bin', 'python'), '-m', 'pip', 'freeze'], stdout=req_file)
            click.secho('Requirements File Updated', fg='green')
        except subprocess.CalledProcessError as e:
            if self.verbose >= 2:
                click.secho(e.__str__(), fg='yellow')
            self.__ctx__.fail(colored('Failed to update pip requirements.', 'red', attrs=['bold']))
