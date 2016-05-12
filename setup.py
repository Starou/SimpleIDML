import os
from distutils.core import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="SimpleIDML",
    version="0.92.5",
    license='BSD Licence',
    author='Stanislas Guerra',
    author_email='stanislas.guerra@gmail.com',
    description='A library to manipulate Adobe(r) IDML(r) files.',
    long_description=README,
    package_dir={'': 'src'},
    install_requires=['lxml>=1.3', 'mock', 'suds'],
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
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Printing',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
