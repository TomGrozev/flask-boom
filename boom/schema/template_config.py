import re

from schema import Schema, And, Optional, Or

slug_pattern = re.compile("^[a-zA-Z0-9-]{3,}$")
author_name_pattern = re.compile("^[a-zA-Z ]{4,}$")
author_url_pattern = re.compile("^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$")

template_config_schema = Schema({
    "slug": And(str, lambda s: slug_pattern.match(s)),
    "name": And(str, lambda n: len(n) >= 3, error='Name must be at least 3 characters long'),
    "description": And(str, lambda d: len(d) >= 20, error='Description must be at least 20 characters long'),
    "author": And(str, lambda a: author_name_pattern.match(a), error='Author can only contain alphanumeric '
                                                                     'characters and spaces, min length 4'),
    "url": And(str, lambda a: author_url_pattern.match(a), error='URL must be a valid URL'),
    "type": Or('app', 'function', error='Type can only be \'app\' or \'function\''),
    Optional("module_init_func"): str
}, ignore_extra_keys=True)
