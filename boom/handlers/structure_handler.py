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
    verbose: int = 0

    def __init__(self, ctx, root_vars, verbose=0) -> None:
        """
        Initialises Handler with context, vars and verbosity

        :param ctx: Click context
        :param root_vars: Variables
        :param verbose: Verbosity level
        """

        self.__ctx__ = ctx
        self.root_vars = root_vars
        self.verbose = verbose

        self.validate_vars()

    def validate_vars(self) -> bool:
        """
        Validates root vars

        Checks required vars and project root path
        :return bool: If valid
        """

        required_keys = ['project_name', 'project_name_path', 'project_description', 'author_name', 'author_url',
                         'project_root']
        missing = list(set(required_keys) - set(self.root_vars.keys()))
        if len(missing) > 0:
            self.__ctx__.fail(colored('Missing one or more required template variables: %s' % ', '.join(missing), 'red',
                                      attrs=['bold']))
            return False
        if not self.validate_project_root():
            self.__ctx__.fail(colored('Target path is invalid. Could be a permissions error.', 'red', attrs=['bold']))
            return False
        return True

    def validate_project_root(self) -> bool:
        """
        Validate project root path

        :return bool: If project root path exists or is creatable
        """

        if not is_pathname_valid(self.root_vars.get('project_root')) and self.verbose >= 1:
            click.secho('Target is not a valid pathname.', fg='yellow')
            return False
        if not is_path_creatable(self.root_vars.get('project_root')) and self.verbose >= 1:
            if not os.path.exists(self.root_vars.get('project_root')) and self.verbose >= 1:
                click.secho('Target does not exist and is not creatable.', fg='yellow')
                return False
            if not os.path.isdir(self.root_vars.get('project_root')) and self.verbose >= 1:
                click.secho('Target is not a directory and is not creatable.', fg='yellow')
                return False
        return True

    def create_project_structure(self):
        """
        Generates project structure using the selected template
        """
        # Ensure template is selected
        if TemplateHandler.selected_template == {}:
            if len(TemplateHandler.templates) > 0:
                if self.verbose >= 2:
                    click.secho('No template selected, selecting default', fg='yellow')
                TemplateHandler.select_template(TemplateHandler.templates[0])
            else:
                self.__ctx__.fail(colored('No template selected, could not select default', 'red', attrs=['bold']))

        click.secho('########### Creating Project Structure ###########', fg='cyan')
        # Create root directory if it doesn't already exist
        self.create_project_root_if_does_not_exist()

        # Check if directory is not empty and empty if so
        self.empty_if_not(self.root_vars.get('project_root'))

        click.secho('Creating files and folders')
        # Recursively create all files in directory
        self.create_files_for_dir(TemplateHandler.selected_template.get('abs_dir'), self.root_vars.get('project_root'))

        # Save project settings to file
        self.save_project_settings()

    def save_project_settings(self):
        click.secho('########### Saving Project Settings ###########', fg='cyan')
        project_settings = self.root_vars
        project_settings.update(template={k: v for k, v in project_settings.get('template', {}).items() if
                                          k in ['required_packages', 'abs_dir', 'root_dir']})
        project_settings_file = open(os.path.join(self.root_vars.get('project_root'), 'project.boom.json'), "w")
        project_settings_file.write(json.dumps(project_settings))
        project_settings_file.close()
        click.secho('Saved Project Settings to project.boom.json', fg='green')

    def create_project_root_if_does_not_exist(self):
        """
        Creates project root if does not exist
        """

        self.create_dir_if_does_not_exist(self.root_vars.get('project_root'))

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

    def create_files_for_dir(self, template_dir, out_dir):
        """
        Recursively create files and folders in target using template

        :param template_dir:
        :param out_dir:
        :return:
        """
        for filename in os.listdir(template_dir):
            if filename == 'template.boom.json':
                continue
            type = TemplateHandler.selected_template.get('type', 'app')
            allow_render = True
            if type == 'function':
                pass
            else:
                allow_render = self.type_app_create(filename)
            if not allow_render:
                continue
            file_path = os.path.join(template_dir, filename)
            if filename.endswith('.jinja2'):
                filename = filename[:-7]
            target_file_path = os.path.join(out_dir, TemplateHandler.template_filename(filename, self.root_vars))
            # Recursive if is directory
            if os.path.isdir(file_path):
                if os.path.exists(target_file_path):
                    continue
                os.makedirs(target_file_path)
                self.create_files_for_dir(file_path, target_file_path)
                continue
            # Open source
            f = open(file_path, 'r')
            # Get temperated content
            res = TemplateHandler.render_template(file_path, f.read(), self.root_vars)
            # Write output
            out = open(target_file_path, 'w+')
            out.write(res)
            out.close()

    def type_app_create(self, filename):
        if filename == 'app':
            return False
        return True
