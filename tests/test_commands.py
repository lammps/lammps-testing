# LAMMPS regression test driver using Python's unittest
#
# Run with "nosetests -v" in main LAMMPS folder
# Run with "nosetests  --with-xunit" to generate xUnit report file
__author__ = 'Richard Berger'
__email__ = "richard.berger@temple.edu"

import unittest
import os
import glob
from lammps_testing.testrunner import LAMMPSTestCase, SkipTest, LAMMPS_MPI_MODE
from lammps_testing.common import discover_tests

TESTS_DIR=os.path.dirname(os.path.realpath(__file__))


def CreateLAMMPSTestCase(testcase_name, script_paths):
    """ Utility function to generate LAMMPS test case classes with both serial and parallel
        testing functions for each input script"""
    def test_serial(func_name, script_path):
        def test_serial_run(self):
            rc = self.run_script(script_path, test_name=func_name)
            self.assertEqual(rc, 0)
        test_serial_run.__name__ = func_name
        return test_serial_run

    methods = {}

    for script_path in script_paths:
        script_name = os.path.basename(script_path)
        name = '_'.join(script_name.split('.')[1:])
        name = '_'.join(name.split('-'))
        name = '_'.join(name.split('+'))

        func_name = "test_" + name + "_serial"
        methods[func_name] = test_serial(func_name, script_path)

    return type(testcase_name.title() + "TestCase", (LAMMPSTestCase, unittest.TestCase), methods)


# collect all the script files and generate the tests automatically by a recursive search and
# skipping a selection of folders

commands_dir = os.path.join(TESTS_DIR, 'commands')

for name, scripts in discover_tests(commands_dir):
    vars()[name.title() + "TestCase"] = CreateLAMMPSTestCase(name, scripts)

if __name__ == '__main__':
    unittest.main()
