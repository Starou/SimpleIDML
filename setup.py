import os
import sys
from setuptools import setup

# Python 2.7
from io import open

with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
    README = f.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

if sys.version_info.major == 3:
    suds_package = "suds-py3"
else:
    suds_package = "suds"

setup(
    name="SimpleIDML",
    version="1.0.4",
    license='BSD Licence',
    author='Stanislas Guerra',
    author_email='stanislas.guerra@gmail.com',
    description='A library to manipulate Adobe(r) IDML(r) files.',
    long_description=README,
    url='https://github.com/Starou/SimpleIDML',
    project_urls={
        'Source Code': 'https://github.com/Starou/SimpleIDML',
        'Issue Tracker': 'https://github.com/Starou/SimpleIDML/issues',
    },
    package_dir={'': 'src'},
    install_requires=['future', 'lxml', suds_package],
    packages=[
        'simple_idml',
        'simple_idml.indesign',
    ],
    package_data={
        'simple_idml.indesign': [
            'scripts/*.jsx',
        ]
    },
    data_files=[],
    scripts=[
        'src/scripts/simpleidml_create_package_from_dir.py',
        'src/scripts/simpleidml_indesign_save_as.py',
        'src/scripts/simpleidml_indesign_close_all_documents.py',
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Printing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
