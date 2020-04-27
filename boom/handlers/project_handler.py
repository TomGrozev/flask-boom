import json
import os
import re
from typing import Pattern

import click
import inflect
from schema import SchemaError
from termcolor import colored

from boom.handlers.package_handler import PackageHandler
from boom.handlers.structure_handler import StructureHandler
from boom.handlers.template_handler import TemplateHandler
from boom.schema.project_config import project_config_schema

engine = inflect.engine()


def find_last_line_of(start_index, match: Pattern or None, lines):
    """
    Gets the last line of a matched pattern

    :param start_index:
    :param match: pattern
    :param lines:
    :return:
    """
    i = start_index + 1
    if match is not None:
        while match.match(lines[i]) or len(lines[i]) == 0:
            i += 1
    return i


def write_at_marker(lines, line_to_write, match: Pattern or None = None, marker=None, not_exists=True):
    if isinstance(lines, list):
        if marker is None:
            line_index = find_last_line_of(0, match, lines)
        else:
            marker_idx = [i for i, line in enumerate(lines) if marker in line]
            # Marker found
            if len(marker_idx) > 0:
                if not_exists:
                    exists = [i for i, line in enumerate(lines) if line_to_write in line]
                    if len(exists) != 0:
                        return 'exists'
                marker_idx = marker_idx[0]
                line_index = find_last_line_of(marker_idx, match, lines)
            else:
                return 'not_found'
        # Insert at index
        lines.insert(line_index, line_to_write + '\n')
    return lines


def write_lines_to_file(lines, file):
    if not isinstance(lines, list):
        if lines == 'exists':
            click.secho('Module already imported.')
        else:
            click.secho('Could not import module automatically. This will have to be done manually.',
                        fg='yellow', bold=True)
        return
    file.seek(0)
    file.write(''.join(lines))
    file.truncate()


class ProjectHandler:
    __ctx__ = None
    project_root = os.getcwd()
    project_config = {}
    project_template_config = {}
    verbose = 0

    def __init__(self, ctx, verbose=0):
        self.__ctx__ = ctx
        self.verbose = verbose

    def validate_and_set_config(self, root_vars):
        """
        Validates root vars

        Checks required vars and project root path
        :return bool: If valid
        """

        try:
            self.project_config = project_config_schema.validate(root_vars)
        except SchemaError as e:
            self.__ctx__.fail(colored('Invalid Project Config: %s' % e, 'red',
                                      attrs=['bold']))

    def create_project(self, project_root, root_vars):
        self.validate_and_set_config(root_vars)

        if project_root is not None:
            self.project_root = os.path.abspath(project_root)

        self.select_template(self.project_config.get('template').get('slug'))

        structure_handler = StructureHandler(self.__ctx__, root_vars, self.project_root, self.verbose)
        structure_handler.create_project_structure(self.project_template_config)

        self.save_project_settings()

        package_handler = PackageHandler(self.__ctx__, self.project_root, self.verbose)

        # Create project venv
        package_handler.start_venv()

    def save_project_settings(self):
        click.secho('########### Saving Project Settings ###########', fg='cyan')
        project_settings = self.project_config
        project_settings.update(template={"slug": self.project_template_config.get('slug')})
        with open(os.path.join(self.project_root, 'project.boom.json'), "w") as f:
            f.write(json.dumps(project_settings))
            f.close()
        click.secho('Saved Project Settings to project.boom.json', fg='green')

    def select_template(self, template_slug):
        template_handler = TemplateHandler(self.__ctx__, self.verbose)
        try:
            self.project_template_config = template_handler.get_config_for_slug(template_slug)
        except SchemaError as e:
            print(e)
            self.__ctx__.fail(colored('Invalid Template config: %s' % e, 'red',
                                      attrs=['bold']))

    def load_project(self, project_root):
        if project_root is not None:
            self.project_root = os.path.abspath(project_root)
        if self.verbose >= 1:
            click.secho('Loading Project Config', fg='yellow')
        project_config_path = os.path.join(project_root, 'project.boom.json')
        if not os.path.exists(project_config_path):
            self.__ctx__.fail(
                colored(
                    'Could not load project settings. Missing project.boom.json file in %s.' % project_root,
                    'red', attrs=['bold']))
        with open(project_config_path, "r") as f:
            ProjectHandler.project_config = json.loads(f.read())

        # Load Template config
        self.select_template(ProjectHandler.project_config.get('template').get('slug'))

    def generate_module(self, module, name):
        if self.project_root is None:
            self.__ctx__.fail(colored('Could not load project', 'red', attrs=['bold']))
        if self.project_template_config is None:
            self.__ctx__.fail(colored('Could not load project template', 'red', attrs=['bold']))
        click.secho('########### Generating Module [%s] ###########' % name, fg='cyan')
        type = self.project_template_config.get('type', 'app')
        structure_handler = StructureHandler(self.__ctx__, ProjectHandler.project_config, self.project_root,
                                             self.verbose)
        # Add extra variables
        structure_handler.root_vars.update(module_name=name)
        structure_handler.root_vars.update(module_name_plural=engine.plural(name))
        # Paths
        input_module_path, output_module_path = self.__get_module_paths__(type, module, name)
        if not os.path.exists(input_module_path):
            self.__ctx__.fail(colored('Unknown module: %s' % module, 'red', attrs=['bold']))
        structure_handler.create_dir_if_does_not_exist(output_module_path)
        structure_handler.empty_if_not(output_module_path)
        if type == 'app':
            structure_handler.create_files_for_dir(
                input_module_path,
                output_module_path)
            self.register_app(name)
        else:
            source_path = os.path.join(input_module_path, f'{module}.py')  # E.g. route.py
            if not os.path.exists(source_path):
                source_path += '.jinja2'
            structure_handler.create_file(source_path, os.path.join(output_module_path, f'{name}.py'))
            self.register_function(name, module, output_module_path,
                                   structure_handler.root_vars.get('module_name_plural'))
        click.secho('Generation Complete', fg='green', bold=True)

    def __get_module_paths__(self, template_type, module, name):
        """
        Gets the input and output paths

        :param template_type:
        :param module:
        :param name:
        :return: input_module_path, output_module_path
        """
        return os.path.join(self.project_template_config.get('abs_dir'), 'project',
                            module if template_type == 'app' else engine.plural(module)), \
               os.path.join(self.project_root, ProjectHandler.project_config.get('project_name_path'),
                            name if template_type == 'app' else engine.plural(module))

    def register_app(self, name):
        # Register app
        init_func = self.project_template_config.get('module_init_func', 'init_app')
        if init_func is not None:
            # Open target project base init func
            with open(os.path.join(self.project_root, ProjectHandler.project_config.get('project_name_path'),
                                   '__init__.py'), "r+") as f:
                lines = f.readlines()
                new_lines = write_at_marker(lines, line_to_write=f"    {name}.{init_func}",
                                            match=re.compile(f'^(.*){init_func}(.*)$'), marker='[b] Apps')
                new_lines = write_at_marker(new_lines,
                                            line_to_write=f"from {ProjectHandler.project_config.get('project_name_path')} import {name}",
                                            match=re.compile('^(.*)import(.*)$'))
                write_lines_to_file(new_lines, f)

    @staticmethod
    def register_function(name, module, module_path, module_plural=None):
        if module_plural is None:
            module_plural = engine.plural(module)
        # Register module
        if module == 'route':
            module_line = f'app.register_blueprint({module_plural})'
            module_match = re.compile('^(.*)app.register_blueprint(.*)$')
        else:
            return

        # Open target project base init func
        with open(os.path.join(module_path, '__init__.py'), "r+") as f:
            lines = f.readlines()
            new_lines = write_at_marker(lines, line_to_write=f"    {module_line}",
                                        match=module_match, marker='[b] Apps')
            new_lines = write_at_marker(new_lines,
                                        line_to_write=f"from .{name} import {engine.plural(name)}",
                                        match=re.compile('^(.*)import(.*)$'))
            write_lines_to_file(new_lines, f)
