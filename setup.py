from setuptools import setup

with open('VERSION', 'r') as f:
    version = f.read()

setup(name='flask-boom',
      version=version,
      description='Project Generator CLI for flask',
      author='Tom Grozev',
      author_email='enquires@tomgrozev.com',
      packages=['boom', 'boom.utils', 'boom.schema', 'boom.handlers', 'boom.commands'],
      install_requires=[
        'click~=7.1.1',
        'setuptools~=46.1.3',
        'termcolor~=1.1.0',
        'PyInquirer~=1.0.3',
        'Jinja2~=2.11.2',
        'pip~=20.0.2',
        'inflect~=4.1.0',
        'MarkupSafe~=1.1.1',
        'six~=1.14.0',
        'schema~=0.7.2',
        'tabulate~=0.8.7',
      ],
      entry_points={
          'console_scripts': [
              'boom = boom.__main__:cli'
          ]
      }
      )
