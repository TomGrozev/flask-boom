import json
import os

import click
from jinja2 import Template
from termcolor import colored

from boom.utils.path_helper import valid_directory

DO_NOT_TEMPLATE_FILES = ['template.boom.json']


class TemplateHandler:
    """
    Template Handler Class

    Handles templates and associated files, etc.
    """
    __ctx__ = None
    verbose = 0

    # Static
    templates_path: str
    templates = []
    selected_template = {}

    def __init__(self, ctx, verbose=0) -> None:
        """
        Initialises handler with context and verbosity

        :param ctx: Click context
        """

        self.__ctx__ = ctx
        TemplateHandler.templates_path = ctx.obj['TEMPLATES_FOLDER']
        self.verbose = verbose

        self.validate_templates_path()
        self.load_templates()

    def validate_templates_path(self):
        """
        Checks if template path is a valid directory
        """
        if not valid_directory(TemplateHandler.templates_path):
            self.__ctx__.fail(
                colored('Invalid template path: %s' % TemplateHandler.templates_path, 'red', attrs=['bold']))

    def load_template_conf(self, root_dir):
        abs_path = os.path.join(TemplateHandler.templates_path, root_dir)
        if not valid_directory(abs_path):
            self.__ctx__.fail(
                colored('Invalid template path: %s' % abs_path, 'red', attrs=['bold']))
        template_conf = json.loads(open(os.path.join(abs_path, 'template.boom.json'), "r").read())
        if not self.__validate_template_config__(template_conf):
            return None
        template_conf.update(root_dir=root_dir)
        template_conf.update(abs_dir=abs_path)
        # Set required packages
        req_path = os.path.join(abs_path, 'requirements.txt')
        req = []
        if os.path.exists(req_path):
            req = open(req_path, "r").read()
            req = req.split('\n')
        template_conf.update(required_packages=req)
        return template_conf

    @staticmethod
    def select_template(template_config):
        """
        Selects a template to be used
        :param template_config: Config to load
        """
        TemplateHandler.selected_template = template_config

    def load_templates(self):
        """
        Loads available templates

        Skips if templates are already loaded
        """
        if len(TemplateHandler.templates) > 0:
            return
        TemplateHandler.templates = []
        for template in os.listdir(TemplateHandler.templates_path):
            template_config = self.load_template_conf(template)
            if template_config is None:
                continue
            TemplateHandler.templates.append(template_config)

    def __validate_template_config__(self, template_config):
        """
        Validates the template config
        :param template_config: Config to check
        :return bool: If Valid
        """
        required_keys = ['name', 'description', 'author', 'url', 'type']
        missing = list(set(required_keys) - set(template_config.keys()))
        if len(missing) > 0:
            if self.verbose >= 1:
                click.secho('Missing one or more required template config variables: %s' % ', '.join(missing), fg='red',
                            bold=True)
            return False
        return True

    @property
    def template_option_names(self) -> [str]:
        """
        Gets list of template names for options in CLI
        :return [str]: list of strings
        """
        return list(map(lambda t: f"{t.get('name').capitalize()[:10]} - ({t.get('description')[:20]})", self.templates))

    @staticmethod
    def render_template(path, content, template_vars):
        """
        Processes template file and returns processed content

        :param path: Path to file
        :param content: Content to process
        :param template_vars: Variables to use
        :return: Processed content
        """
        _, filename = os.path.split(path)
        if filename in DO_NOT_TEMPLATE_FILES or not filename.endswith('.jinja2'):
            return content
        tm = Template(content)
        return tm.render(**template_vars)

    @staticmethod
    def template_filename(filename, template_vars):
        """
        Templates a filename

        :param filename: Filename to template
        :param template_vars: Variables to use
        :return: Processed filename
        """
        tm = Template(filename)
        return tm.render(**template_vars)
