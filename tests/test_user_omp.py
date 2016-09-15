# LAMMPS regression test driver using Python's unittest
#
# Run with "nosetests -v" in main LAMMPS folder
# Run with "nosetests  --with-xunit" to generate xUnit report file
__author__ = 'Richard Berger'
__email__ = "richard.berger@temple.edu"

import unittest
import os
import sys
import glob
from lammps_testing.testrunner import LAMMPSTestCase, SkipTest, LAMMPS_DIR


def CreateLAMMPSTestCaseOMP(testcase_name, script_names):
    """ Utility function to generate LAMMPS test case classes for OpenMP
        testing functions for each input script"""
    def setUp(self):
        self.cwd = os.path.join(LAMMPS_DIR, "test-user-omp", testcase_name)

    def test_parallel_omp(script_name, nprocs, nthreads, log):
        def test_parallel_omp_run(self):
            rc = self.run_script(script_name, nprocs=nprocs, nthreads=nthreads, log=log)
            self.assertEqual(rc, 0)
        return test_parallel_omp_run

    methods = {"setUp": setUp}

    for script_name in script_names:
        name = '_'.join(script_name.split('.')[1:])
        name = '_'.join(name.split('-'))
        name = '_'.join(name.split('+'))

        for nthreads in [1, 2, 4, 8]:
            for nprocs in [1, 2, 4, 8]:
                if nthreads * nprocs > 8: continue

                log_filename = "log.%dxOpenMP_%dxMPI" % (nthreads, nprocs)
                test_name = "test_%s_%d_omp_%d_mpi" % (name, nthreads, nprocs)

                methods[test_name] = test_parallel_omp(script_name, nprocs=nprocs, nthreads=nthreads, log=log_filename)

    return type(testcase_name.title() + "TestCase", (LAMMPSTestCase, unittest.TestCase), methods)




# collect all the script files and generate the tests automatically by a recursive search and
# skipping a selection of folders

test_user_omp_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'legacy', 'test-user-omp'))

skip_list = []

for name in os.listdir(test_user_omp_dir):
    path = os.path.join(test_user_omp_dir, name)
    print(name)

    if name in skip_list:
        continue

    # for now only use the lower case examples (=simple ones)

    if name.islower() and os.path.isdir(path):
        script_names = map(os.path.basename, glob.glob(os.path.join(path, 'in.*')))
        vars()[name.title() + "TestCase"] = CreateLAMMPSTestCaseOMP(name, script_names)

if __name__ == '__main__':
    unittest.main()
