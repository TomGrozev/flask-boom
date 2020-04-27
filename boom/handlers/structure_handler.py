import json
import os
import shutil

import click
from termcolor import colored

from boom.handlers.template_handler import TemplateHandler
from boom.utils.path_helper import is_pathname_valid, is_path_creatable, valid_directory


class StructureHandler:
    """
    Structure Handler class

    Handles project structure operations, e.g. creating files, deleting files, etc
    """
    __ctx__ = None
    root_vars: dict = {}
    project_root = os.getcwd()
    verbose: int = 0

    def __init__(self, ctx, root_vars: object, project_root: str, verbose=0) -> None:
        """
        Initialises Handler with context, vars and verbosity

        :param ctx: Click context
        :param root_vars: Variables
        :param verbose: Verbosity level
        """

        self.__ctx__ = ctx
        self.root_vars = root_vars
        self.project_root = project_root
        self.verbose = verbose

        if not self.validate_project_root():
            self.__ctx__.fail(
                colored('Target path is invalid. Could be a file system permissions error.', 'red', attrs=['bold']))

    def validate_project_root(self) -> bool:
        """
        Validate project root path

        :return bool: If project root path exists or is creatable
        """

        if not is_pathname_valid(self.project_root):
            if self.verbose >= 1:
                click.secho('Target is not a valid pathname.', fg='yellow')
            return False
        if not is_path_creatable(self.project_root):
            if not os.path.exists(self.project_root):
                if not is_path_creatable(os.path.dirname(self.project_root)):
                    if self.verbose >= 1:
                        click.secho('Target does not exist and is not creatable.', fg='yellow')
                    return False
            elif not os.path.isdir(self.project_root):
                if self.verbose >= 1:
                    click.secho('Target is not a directory and is not creatable.', fg='yellow')
                return False
        return True

    def create_project_structure(self, selected_template_config):
        """
        Generates project structure using the selected template
        """
        # Ensure template is selected
        if not TemplateHandler.validate_template_config(selected_template_config):
            self.__ctx__.fail(colored('No template selected', 'red', attrs=['bold']))
            return

        click.secho('########### Creating Project Structure ###########', fg='cyan')
        # Create root directory if it doesn't already exist
        self.create_project_root_if_does_not_exist()

        # Check if directory is not empty and empty if so
        self.empty_if_not(self.project_root)

        click.secho('Creating files and folders')
        # Recursively create all files in directory
        self.create_files_for_dir(selected_template_config.get('abs_dir'), self.project_root,
                                  root=True, type=selected_template_config.get('type', 'app'))

    def create_project_root_if_does_not_exist(self):
        """
        Creates project root if does not exist
        """

        self.create_dir_if_does_not_exist(self.project_root)

    def create_dir_if_does_not_exist(self, target_dir):
        """
        Creates target directory if does not exist
        """
        if not os.path.exists(target_dir):
            if self.verbose >= 1:
                click.secho('Target directory does not exist, creating.', fg='yellow')
            os.makedirs(target_dir)

    def empty_if_not(self, target_dir):
        if len(os.listdir(target_dir)) > 0:
            click.confirm(colored('The target directory is not empty, continuing with overwrite files. Do you want to '
                                  'continue?', 'red', attrs=['bold']), abort=True, err=True)
            click.secho('Emptying Directory')

            # Clear directory
            self.empty_directory(target_dir)

    def empty_directory(self, target_dir):
        """
        Empty a directory

        :param target_dir: Path of directory to empty
        :return:
        """

        # Check directory exists and is directory
        if not valid_directory(target_dir):
            self.__ctx__.fail(
                colored('Failed to clear contents of target directory. Directory does not exists or path may be a '
                        'file', 'red', attrs=['bold']))
            return
        if self.verbose >= 1:
            click.secho('Emptying target directory', fg='yellow')
        for filename in os.listdir(target_dir):
            file_path = os.path.join(target_dir, filename)
            if self.verbose >= 2:
                click.secho('Attempting to delete %s' % file_path, fg='yellow')
            # Try delete file or directory
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                if self.verbose >= 1:
                    click.secho('Failed to %s. Reason: %s' % (file_path, e), fg='yellow')
                self.__ctx__.fail(colored('Failed to clear contents of target directory', 'red', attrs=['bold']))
        click.secho('Directory Emptied', fg='green')

    def create_files_for_dir(self, template_dir, out_dir, root=False, type='app'):
        """
        Recursively create files and folders in target using template

        :param root:
        :param template_dir:
        :param out_dir:
        :return:
        """
        for filename in os.listdir(template_dir):
            if filename == 'template.boom.json':
                continue
            allow_render = True
            if type == 'function':
                pass
            else:
                allow_render = self.type_app_create(filename)
            if not allow_render:
                continue
            template_file_path = os.path.join(template_dir, filename)
            if filename.endswith('.jinja2'):
                filename = filename[:-7]
            if os.path.isdir(template_file_path) and filename == 'project' and root:
                filename = self.root_vars.get('project_name_path')
            target_file_path = os.path.join(out_dir, filename)
            # Recursive if is directory
            if os.path.isdir(template_file_path):
                if os.path.exists(target_file_path):
                    continue
                os.makedirs(target_file_path)
                self.create_files_for_dir(template_file_path, target_file_path)
                continue
            self.create_file(template_file_path, target_file_path)

    def create_file(self, source_file_path, target_file_path):
        if not is_pathname_valid(source_file_path) or not os.path.exists(source_file_path) or \
                not os.path.isfile(source_file_path) or not is_pathname_valid(target_file_path):
            self.__ctx__.fail(
                colored('File path is invalid. Could be a file system permissions error.', 'red', attrs=['bold']))
            return
        with open(source_file_path, 'r') as source_file:
            res = TemplateHandler.render_template(source_file_path, source_file.read(), self.root_vars)
            with open(target_file_path, 'w+') as out_file:
                out_file.write(res)
                out_file.close()

    def type_app_create(self, filename):
        if filename == 'app':
            return False
        return True
