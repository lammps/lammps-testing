from setuptools import setup
from glob import glob
import os

setup(name='lammps_testing',
    version='1.0.0',
    description='Utilities to run LAMMPS tests',
    url='https://github.com/lammps/lammps-testing',
    author='Richard Berger',
    author_email='richard.berger@outlook.com',
    license='GPL',
    packages=['lammps_testing'],
    entry_points = {
        "console_scripts": ['lammps_run_tests = lammps_testing.run_tests:main',
                            'lammps_generate_regression_xml  = lammps_testing.generate_regression_xml:main',
                            'lammps_regression_tests = lammps_testing.regression:main',
                            'lammps_test = lammps_testing.lammps_test:main',
                            'lammps_run_regression_test = lammps_testing.run_regression_test:main'
                           ]
    },
    install_requires=[
        'nose',
        'gcovr',
        'termcolor',
        'matplotlib',
        'pyyaml',
        'Jinja2',
        'coverage',
        'devpi'
    ]
)
