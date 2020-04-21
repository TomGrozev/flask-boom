from setuptools import setup

setup(name='flask-boom',
      version='0.1.0',
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
