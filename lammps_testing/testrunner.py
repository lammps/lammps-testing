# LAMMPS regression test driver using Python's unittest
from __future__ import print_function
__author__ = 'Richard Berger'
__email__ = "richard.berger@temple.edu"

import unittest
import os
import sys
from datetime import datetime
from subprocess import call

# Before running any tests these two environment variables must be set

# full path of LAMMPS main directory
LAMMPS_DIR=os.environ['LAMMPS_DIR']

# full path of LAMMPS binary being tested
LAMMPS_BINARY=os.environ['LAMMPS_BINARY']

# one of openmpi, mpich
LAMMPS_MPI_MODE=os.environ.get('LAMMPS_MPI_MODE', 'openmpi')

# test modes separated by colons. e.g. serial:parallel:omp:valgrind
LAMMPS_TEST_MODES=os.environ.get('LAMMPS_TEST_MODES', 'serial').split(':')

# list of folders which should be scanned for tests
LAMMPS_TEST_DIRS=os.environ.get('LAMMPS_TEST_DIRS', '').split(':')


class LAMMPSTestCase:
    """ Mixin class for each LAMMPS test case. Defines utility function to run in serial or parallel"""
    def run_script(self, script_name, nprocs=1, nthreads=1, ngpus=1, screen=True, log=None, launcher=[], force_openmp=False, force_mpi=False, force_gpu=False, force_kokkos=False, force_cuda=False):
        if screen:
            output_options = []
        else:
            output_options = ["-screen", "none"]

        if log:
            output_options += ["-log", log]

        exe = launcher + [LAMMPS_BINARY]

        mpi_options = []
        lammps_options = ["-in", script_name] + output_options

        if nthreads > 1 and force_openmp:
            lammps_options += ["-sf", "omp", "-pk", "omp", str(nthreads)]

        if force_kokkos:
            lammps_options += ["-k", "on"]
            if nthreads > 1:
                lammps_options += ["t", str(nthreads)]
            if force_cuda:
                lammps_options += ["g", str(ngpus)]
            lammps_options += ["-sf", "kk", "-pk", "kokkos newton on neigh half"]

        if force_gpu:
            lammps_options += ["-pk", "gpu", "1", "-sf", "gpu"]

        if nprocs > 1 or force_mpi:
            mpi_options = ["mpirun", "-np", str(nprocs)]
            if LAMMPS_MPI_MODE == "openmpi":
                mpi_options += ["-x", "OMP_NUM_THREADS="+str(nthreads)]
            elif LAMMPS_MPI_MODE == "mpich":
                mpi_options += ["-env", "OMP_NUM_THREADS", str(nthreads)]

        test_name = type(self).__name__
        outfile_path = os.path.join(self.cwd, f"{test_name}_stdout.log")
        errfile_path = os.path.join(self.cwd, f"{test_name}_stderr.log")

        start_time = datetime.now()

        with open(outfile_path, "w+") as outfile, open(errfile_path, "w+") as errfile:
            retcode = call(mpi_options + exe + lammps_options, cwd=self.cwd, stdout=outfile, stderr=errfile)

        end_time = datetime.now()
        duration = end_time - start_time

        print(f"Completed in: {duration.total_seconds()} seconds")

        # output for JUnit attachment plugin
        print(f"[[ATTACHMENT|{outfile_path}]]")
        print(f"[[ATTACHMENT|{errfile_path}]]")

        return retcode


def SkipTest(cls, func_name, reason):
    """ utility function to skip a specific test for a reason """
    setattr(cls, func_name, unittest.skip(reason)(getattr(cls, func_name)))
