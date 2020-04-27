import re

from schema import Schema, And

from boom.schema.template_config import template_config_schema

project_name_pattern = re.compile("^[a-zA-Z][a-zA-Z0-9 ]{2,}$")
project_name_path_pattern = re.compile("^[a-zA-Z0-9_]{3,}$")
author_name_pattern = re.compile("^[a-zA-Z ]{4,}$")
author_url_pattern = re.compile("^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$")

project_config_schema = Schema({
    "project_name": And(str, lambda p: project_name_pattern.match(p),
                        error='Project Name must start with a letter and can only contain alphanumeric '
                              'characters and spaces, min length 3'),
    "project_name_path": And(str, lambda p: project_name_path_pattern.match(p),
                             error='Project Path Name must only contain alphanumeric characters or '
                                   'underscores, min length 3'),
    "project_description": And(str, lambda d: len(d) >= 20, error='Description must be at least 20 characters long'),
    "author_name": And(str, lambda a: author_name_pattern.match(a), error='Author Name can only contain alphanumeric '
                                                                          'characters and spaces, min length 4'),
    "author_url": And(str, lambda a: author_url_pattern.match(a), error='Author URL must be a valid URL'),
    "template": template_config_schema
}, ignore_extra_keys=True)
