from setuptools import setup

setup(
    name="dove",
    version='0.0.3',
    description='Docker Versioning Extension',
    long_description='A tool to extend the docker functionality to include an incremental tag versioning system for docker images',
    license='Apache 2.0',
    author='Usman Shahid',
    author_email='u.manshahid@gmail.com',
    py_modules=['dove'],
    install_requires=[
      'Click==6.7',
    ],
    entry_points={
      'console_scripts': [
        'dove=dove:cli'
      ]
    }
)
