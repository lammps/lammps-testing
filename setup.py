from setuptools import setup

setup(name='LAMMPS Testing Utilities',
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
                              'lammps_regression_tests = lammps_testing.regression:main ']
      },
)
