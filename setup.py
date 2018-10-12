from setuptools import setup

setup(
    name="dove-docker",
    version='0.0.4',
    description='A tool to extend the docker functionality to include an incremental tag versioning system for docker images',
    license='Apache 2.0',
    author='Usman Shahid',
    author_email='u.manshahid@gmail.com',
    url='https://github.com/intech-iiot/dove', 
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