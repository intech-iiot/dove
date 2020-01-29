from setuptools import setup

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
  long_description = f.read()

setup(
    name="dove-docker",
    version='0.0.6',
    description='A tool to extend the docker functionality to include an incremental tag versioning system for docker images',
    license='Apache 2.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Usman Shahid',
    author_email='u.manshahid@gmail.com',
    url='https://github.com/intech-iiot/dove', 
    py_modules=['dove'],
    install_requires=[
      'click==7.0',
    ],
    entry_points={
      'console_scripts': [
        'dove=dove:cli'
      ]
    }
)
