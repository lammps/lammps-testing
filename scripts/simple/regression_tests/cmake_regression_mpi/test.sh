#!/bin/bash
export WORKING_DIR=$PWD
SCRIPTDIR="$(dirname "$(realpath "$0")")"

# copy tests
rsync -a --delete $LAMMPS_TESTING_DIR/tests .

source pyenv/bin/activate

export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"

if [ "$HOSTNAME" = atlas2 ]; then
    taskset -pc 0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30 $$
fi

rm *.out *.xml || true

export LAMMPS_TEST_EXCLUDE=(
                            ASPHERE
                            COUPLE
                            HEAT
                            USER/atc
                            USER/cg-cmm
                            USER/dpd/dpdrx-shardlow
                            USER/eff
                            USER/fep
                            USER/lb
                            USER/mgpt
                            USER/misc/grem
                            USER/misc/i-pi
                            USER/misc/imd
                            USER/misc/pimd
                            USER/quip
                            VISCOSITY
                            accelerate
                            balance
                            gcmc
                            kim
                            mscg
                            neb
                            nemd
                            prd
                            tad
                           )

# Run regression tests
lammps_regression_tests 8 "mpiexec -np 8 ${LAMMPS_BINARY} -v CORES 8" tests/examples -exclude ${LAMMPS_TEST_EXCLUDE[@]} 2>&1 |tee test0.out
lammps_regression_tests 8 "mpiexec -np 8 ${LAMMPS_BINARY} -partition 4x2 -v CORES 8" tests/examples -only prd 2>&1 |tee test1.out

# generate regression XML
lammps_generate_regression_xml --test-dir ${PWD}/tests/ --log-file test0.out --out-file regression_00.xml
lammps_generate_regression_xml --test-dir ${PWD}/tests/ --log-file test1.out --out-file regression_01.xml

deactivate
