import json
import os

import click
import inflect
from termcolor import colored

from boom.handlers.structure_handler import StructureHandler
from boom.handlers.template_handler import TemplateHandler

engine = inflect.engine()


def find_last_line_of(start_index, search_string, lines):
    i = start_index + 1
    while search_string in lines[i] or len(lines[i]) == 0:
        i += 1
        print(lines[i])
    return i


class ProjectHandler:
    __ctx__ = None
    project_root = os.getcwd()
    project_config = {}
    verbose = 0

    def __init__(self, ctx, project_root=None, verbose=0):
        self.__ctx__ = ctx
        self.verbose = verbose
        if project_root is not None:
            self.project_root = os.path.abspath(project_root)
        self.load_project()

    def load_project(self):
        if self.verbose >= 1:
            click.secho('Loading Project Config', fg='yellow')
        project_config_path = os.path.join(self.project_root, 'project.boom.json')
        if not os.path.exists(project_config_path):
            self.__ctx__.fail(
                colored(
                    'Could not load project settings. Missing project.boom.json file in %s.' % self.project_root,
                    'red', attrs=['bold']))
        ProjectHandler.project_config = json.loads(open(project_config_path, "r").read())

        # Load Template config
        template_handler = TemplateHandler(self.__ctx__, self.verbose)
        template_handler.select_template(
            template_handler.load_template_conf(ProjectHandler.project_config.get('template').get('root_dir')))

    def generate_module(self, module, name):
        click.secho('########### Generating Module [%s] ###########' % name, fg='cyan')
        structure_handler = StructureHandler(self.__ctx__, ProjectHandler.project_config, self.verbose)
        # Add extra variables
        structure_handler.root_vars.update(module_name=name)
        structure_handler.root_vars.update(module_name_plural=engine.plural(name))
        if TemplateHandler.selected_template.get('type') == 'app':
            module_path = os.path.join(self.project_root, ProjectHandler.project_config.get('project_name_path'), name)
            structure_handler.create_dir_if_does_not_exist(module_path)
            structure_handler.empty_if_not(module_path)
            structure_handler.create_files_for_dir(
                os.path.join(TemplateHandler.selected_template.get('abs_dir'), '{{project_name_path}}', module),
                module_path)
            # Register app in app.py
            init_func = TemplateHandler.selected_template.get('module_init')
            if init_func is not None:
                with open(os.path.join(self.project_root, ProjectHandler.project_config.get('project_name_path'),
                                       '__init__.py'), "r+") as f:
                    lines = f.readlines()
                    apps_idx = [i for i, line in enumerate(lines) if '[b] Apps' in line]
                    if len(apps_idx) > 0:
                        module_line_str = f"{name}.{init_func}"
                        module_idx = [i for i, line in enumerate(lines) if module_line_str in line]
                        if len(module_idx) == 0:
                            apps_idx = apps_idx[0]
                            app_import_index = find_last_line_of(0, 'import', lines)
                            app_line_index = find_last_line_of(apps_idx, init_func, lines) + 1
                            # Insert at indexes
                            lines.insert(app_import_index,
                                         f"from {ProjectHandler.project_config.get('project_name_path')} import {name}\n")
                            lines.insert(app_line_index, '    ' + module_line_str + '\n')
                            f.seek(0)
                            f.write(''.join(lines))
                            f.truncate()
                        else:
                            click.secho('Module already imported.')
                    else:
                        click.secho('Could not import module automatically. This will have to be done manually.', fg='yellow', bold=True)
        click.secho('Generation Complete', fg='green', bold=True)
