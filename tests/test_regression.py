# LAMMPS regression test driver using Python's unittest
#
# Run with "nosetests -v" in main LAMMPS folder
# Run with "nosetests  --with-xunit" to generate xUnit report file
__author__ = 'Richard Berger'
__email__ = "richard.berger@temple.edu"

import unittest
import os
import glob
from lammps_testing.testrunner import LAMMPSRegressionTestCase, SkipTest
from lammps_testing.common import discover_tests

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))

def CreateLAMMPSTestCase(testcase_name, script_names):
    """ Utility function to generate LAMMPS test case classes with both serial and parallel
        testing functions for each input script"""
    def setUp(self):
        self.cwd = os.path.join(TESTS_DIR, "examples", testcase_name)

    def test_regression(func_name, script_name):
        def test_regression_run(self):
            rc = self.run_regression(script_name, test_name=func_name)
            self.assertEqual(rc, 0)
        test_regression_run.__name__ = func_name
        return test_regression_run

    methods = {"setUp": setUp}

    for script_name in script_names:
        name = '_'.join(script_name.split('.')[1:])
        name = name.replace('-', '_')

        func_name = "test_" + name + "_regression"
        methods[func_name] = test_regression(func_name, script_name)

    return type(testcase_name.title() + "TestCase", (LAMMPSRegressionTestCase, unittest.TestCase), methods)


# collect all the script files and generate the tests automatically by a recursive search and
# skipping a selection of folders

examples_dir = os.path.join(TESTS_DIR, 'examples')

skip_list = [
    'ASPHERE',
    'COUPLE',
    'HEAT',
    'USER/atc',
    'USER/cg-cmm',
    'USER/dpd/dpdrx-shardlow',
    'USER/eff',
    'USER/fep',
    'USER/lb',
    'USER/mgpt',
    'USER/misc/grem',
    'USER/misc/i-pi',
    'USER/misc/imd',
    'USER/misc/pimd',
    'USER/quip',
    'VISCOSITY',
    'accelerate',
    'balance',
    'gcmc',
    'kim',
    'mscg',
    'neb',
    'nemd',
    'prd',
    'tad'
]

for name, scripts in discover_tests(examples_dir, skip_list):
    name = name.replace('/', '.')
    name = name.replace('-', '_')
    vars()[name.title() + "TestCase"] = CreateLAMMPSTestCase(name, scripts)

if __name__ == '__main__':
    unittest.main()
