from setuptools import setup

with open('VERSION', 'r') as f:
    version = f.read()

setup(name='flask-boom',
      version=version,
      description='Project Generator CLI for flask',
      author='Tom Grozev',
      author_email='enquires@tomgrozev.com',
      packages=['boom'],
      install_requires=[
          'Click'
      ],
      entry_points={
          'console_scripts': [
              'boom = boom.__main__:cli'
          ]
      }
      )
