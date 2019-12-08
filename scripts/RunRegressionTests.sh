#!/bin/bash
SCRIPTDIR="$(dirname "$(realpath "$0")")"

. $SCRIPTDIR/LAMMPSTesting.sh

export LAMMPS_TEST_EXCLUDE=(
                            USER/eff
                            USER/misc/imd
                            USER/lb
                            HEAT
                            COUPLE
                            USER/fep
                            kim
                            gcmc
                            mscg
                            nemd
                            prd
                            tad
                            neb
                            VISCOSITY
                            ASPHERE
                            USER/mgpt
                            USER/dpd/dpdrx-shardlow
                            balance
                            accelerate
                            USER/atc
                            USER/quip
                            USER/misc/grem
                            USER/misc/i-pi
                            USER/misc/pimd
                            USER/cg-cmm
                           )

source $LAMMPS_BUILD_DIR/pyenv/bin/activate

rm *.out *.xml || true

# Run regression tests
lammps_regression_tests 8 "mpiexec -np 8 ${LAMMPS_BINARY} -v CORES 8" $LAMMPS_TESTING_DIR/tests/examples -exclude ${LAMMPS_TEST_EXCLUDE[@]} 2>&1 |tee test0.out
lammps_regression_tests 8 "mpiexec -np 8 ${LAMMPS_BINARY} -partition 4x2 -v CORES 8" $LAMMPS_TESTING_DIR/tests/examples -only prd 2>&1 |tee test1.out

# generate regression XML
lammps_generate_regression_xml --test-dir $PWD/lammps-testing/tests/ --log-file test0.out --out-file regression_00.xml
lammps_generate_regression_xml --test-dir $PWD/lammps-testing/tests/ --log-file test1.out --out-file regression_01.xml

deactivate
