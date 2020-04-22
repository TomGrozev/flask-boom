import json
import os

import click
import inflect
from termcolor import colored

from boom.handlers.structure_handler import StructureHandler
from boom.handlers.template_handler import TemplateHandler

engine = inflect.engine()


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
            module_path = os.path.join(self.project_root, name)
            structure_handler.create_dir_if_does_not_exist(module_path)
            structure_handler.empty_if_not(module_path)
            structure_handler.create_files_for_dir(
                os.path.join(TemplateHandler.selected_template.get('abs_dir'), '{{project_name_path}}', module),
                module_path)
        click.secho('Generation Complete', fg='green', bold=True)
