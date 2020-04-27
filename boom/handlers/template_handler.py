import json
import os

import click
from jinja2 import Template
from schema import SchemaError
from termcolor import colored

from boom.schema.template_config import template_config_schema
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

    def __init__(self, ctx, verbose=0) -> None:
        """
        Initialises handler with context and verbosity

        :param ctx: Click context
        """

        self.__ctx__ = ctx
        TemplateHandler.templates_path = ctx.obj['TEMPLATES_FOLDER']
        self.verbose = verbose

        self.validate_templates_path()
        if len(TemplateHandler.templates) == 0:
            self.load_templates()

    def validate_templates_path(self):
        """
        Checks if template path is a valid directory
        """
        if not valid_directory(TemplateHandler.templates_path):
            self.__ctx__.fail(
                colored('Invalid template path: %s' % TemplateHandler.templates_path, 'red', attrs=['bold']))

    def get_config_for_slug(self, slug, fresh=False):
        if fresh:
            self.load_templates()
        for template in TemplateHandler.templates:
            if template.get('slug') == slug:
                return template
        return None

    def load_template_conf(self, root_dir):
        abs_path = os.path.join(TemplateHandler.templates_path, root_dir)
        if not valid_directory(abs_path):
            if self.verbose >= 1:
                click.secho('Invalid template path: %s' % abs_path, fg='yellow')
            return None
        with open(os.path.join(abs_path, 'template.boom.json'), "r") as f:
            template_conf = json.loads(f.read())
            f.close()
            try:
                template_conf = self.validate_template_config(template_conf)
            except SchemaError as e:
                if self.verbose >= 1:
                    click.secho('Invalid Template config: %s' % e, fg='yellow')
                return None
            # These variables are not saved but are just easier than keep checking
            template_conf.update(root_dir=root_dir)
            template_conf.update(abs_dir=abs_path)
            # Set required packages
            req = self.load_requirements(abs_path)
            template_conf.update(required_packages=req)
            return template_conf

    @staticmethod
    def load_requirements(template_path):
        req_path = os.path.join(template_path, 'requirements.txt')
        req = []
        if os.path.exists(req_path):
            with open(req_path, "r") as f:
                # TODO: Strip versions?
                req = f.read().split('\n')
        return req

    def load_templates(self):
        """
        Loads available templates

        Skips if templates are already loaded
        """
        TemplateHandler.templates = []
        for template in os.listdir(TemplateHandler.templates_path):
            template_config = self.load_template_conf(template)
            if template_config is None:
                continue
            TemplateHandler.templates.append(template_config)

    @staticmethod
    def validate_template_config(template_config):
        """
        Validates the template config
        :param template_config: Config to check
        :return bool: valid template config
        """
        return template_config_schema.validate(template_config)

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
