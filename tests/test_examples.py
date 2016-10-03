# LAMMPS regression test driver using Python's unittest
#
# Run with "nosetests -v" in main LAMMPS folder
# Run with "nosetests  --with-xunit" to generate xUnit report file
__author__ = 'Richard Berger'
__email__ = "richard.berger@temple.edu"

import unittest
import os
import glob
from lammps_testing.testrunner import LAMMPSTestCase, SkipTest, LAMMPS_DIR, LAMMPS_MPI_MODE, LAMMPS_TEST_MODES


def CreateLAMMPSTestCase(testcase_name, script_names):
    """ Utility function to generate LAMMPS test case classes with both serial and parallel
        testing functions for each input script"""
    def setUp(self):
        self.cwd = os.path.join(LAMMPS_DIR, "examples", testcase_name)

    def test_serial(func_name, script_name):
        def test_serial_run(self):
            rc = self.run_script(script_name)
            self.assertEqual(rc, 0)
        test_serial_run.__name__ = func_name
        return test_serial_run

    def test_parallel(func_name, script_name):
        def test_parallel_run(self):
            rc = self.run_script(script_name, nprocs=4)
            self.assertEqual(rc, 0)
        test_parallel_run.__name__ = func_name
        return test_parallel_run

    def test_parallel_omp(func_name, script_name):
        def test_parallel_omp_run(self):
            rc = self.run_script(script_name, nthreads=4)
            self.assertEqual(rc, 0)
        test_parallel_omp_run.__name__ = func_name
        return test_parallel_omp_run

    def test_serial_valgrind(name, script_name):
        valgrind_exec = ["valgrind", "--leak-check=full", "--xml=yes", "--xml-file=" + name + ".memcheck"]

        if LAMMPS_MPI_MODE == "openmpi" and os.path.exists("/usr/share/openmpi/openmpi-valgrind.supp"):
            valgrind_exec += ["--suppressions=/usr/share/openmpi/openmpi-valgrind.supp"]

        def test_serial_valgrind_run(self):
            rc = self.run_script(script_name,launcher=valgrind_exec)
            self.assertEqual(rc, 0)
        test_serial_valgrind_run.__name__ = func_name
        return test_serial_valgrind_run

    methods = {"setUp": setUp}

    for script_name in script_names:
        name = '_'.join(script_name.split('.')[1:])

        if 'serial' in LAMMPS_TEST_MODES:
            func_name = "test_" + name + "_serial"
            methods[func_name] = test_serial(func_name, script_name)

        if 'parallel' in LAMMPS_TEST_MODES:
            func_name = "test_" + name + "_parallel"
            methods[func_name] = test_parallel(func_name, script_name)

        if 'omp' in LAMMPS_TEST_MODES:
            func_name = "test_" + name + "_parallel_omp"
            methods[func_name] = test_parallel_omp(func_name, script_name)

        if 'valgrind' in LAMMPS_TEST_MODES:
            func_name = "test_" + name + "_serial_valgrind"
            methods[func_name] = test_serial_valgrind(func_name, name, script_name)

    return type(testcase_name.title() + "TestCase", (LAMMPSTestCase, unittest.TestCase), methods)


# collect all the script files and generate the tests automatically by a recursive search and
# skipping a selection of folders

examples_dir = os.path.join(LAMMPS_DIR, 'examples')

skip_list = ['accelerate', 'hugoniostat', 'kim', 'neb', 'python', 'reax', 'rerun', 'tad']

for name in os.listdir(examples_dir):
    path = os.path.join(examples_dir, name)

    if name in skip_list:
        continue

    # for now only use the lower case examples (=simple ones)

    if name.islower() and os.path.isdir(path):
        script_names = map(os.path.basename, glob.glob(os.path.join(path, 'in.*')))
        vars()[name.title() + "TestCase"] = CreateLAMMPSTestCase(name, script_names)

if 'omp' in LAMMPS_TEST_MODES:
    SkipTest(CombTestCase, "test_comb3_parallel_omp", "comb3 currently not supported by USER-OMP")

if 'parallel' in LAMMPS_TEST_MODES:
    SkipTest(BalanceTestCase, "test_balance_bond_fast_parallel", "Crashes randomly")

if __name__ == '__main__':
    unittest.main()
