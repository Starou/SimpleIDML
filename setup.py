from distutils.core import setup
import os
import sys


setup(
    name="SimpleIDML",
    version="0.91.1",
    author='Stanislas Guerra',
    author_email='stanislas.guerra@gmail.com',
    description='',
    long_description='',
    package_dir={'': 'src'},
    packages=['simple_idml'],
    data_files=[],
    scripts=[
        'src/scripts/simpleidml_create_package_from_dir.py',
    ],
)
