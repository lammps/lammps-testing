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

TESTS_DIR=os.path.dirname(os.path.realpath(__file__))


def CreateLAMMPSTestCase(testcase_name, script_names):
    """ Utility function to generate LAMMPS test case classes with both serial and parallel
        testing functions for each input script"""
    def setUp(self):
        self.cwd = os.path.join(TESTS_DIR, "commands", testcase_name)

    def test_serial(func_name, script_name):
        def test_serial_run(self):
            rc = self.run_script(script_name)
            self.assertEqual(rc, 0)
        test_serial_run.__name__ = func_name
        return test_serial_run

    methods = {"setUp": setUp}

    for script_name in script_names:
        name = '_'.join(script_name.split('.')[1:])
        name = '_'.join(name.split('-'))
        name = '_'.join(name.split('+'))

        func_name = "test_" + name + "_serial"
        methods[func_name] = test_serial(func_name, script_name)

    return type(testcase_name.title() + "TestCase", (LAMMPSTestCase, unittest.TestCase), methods)


# collect all the script files and generate the tests automatically by a recursive search and
# skipping a selection of folders

commands_dir = os.path.join(TESTS_DIR, 'commands')

skip_list = []

for name in os.listdir(commands_dir):
    path = os.path.join(commands_dir, name)
    print(name)

    if name in skip_list:
        continue

    if os.path.isdir(path):
        script_names = map(os.path.basename, glob.glob(os.path.join(path, 'in.*')))
        vars()[name.title() + "TestCase"] = CreateLAMMPSTestCase(name, script_names)

if __name__ == '__main__':
    unittest.main()
