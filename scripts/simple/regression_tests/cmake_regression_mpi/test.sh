#!/bin/bash
export WORKING_DIR=$PWD
SCRIPTDIR="$(dirname "$(realpath "$0")")"

# copy tests
rsync -a --delete $LAMMPS_TESTING_DIR/tests .

source pyenv/bin/activate

export LD_LIBRARY_PATH=$VIRTUAL_ENV/lib64:$VIRTUAL_ENV/lib:$LD_LIBRARY_PATH
export LAMMPS_BINARY=${VIRTUAL_ENV}/bin/lmp
export LAMMPS_POTENTIALS="${VIRTUAL_ENV}/share/lammps/potentials"

rm *.out *.xml || true

# Run regression tests
#lammps_regression_tests 8 "mpiexec -np 8 ${LAMMPS_BINARY} -v CORES 8" tests/examples -exclude ${LAMMPS_TEST_EXCLUDE[@]} 2>&1 |tee test0.out
#lammps_regression_tests 8 "mpiexec -np 8 ${LAMMPS_BINARY} -partition 4x2 -v CORES 8" tests/examples -only prd 2>&1 |tee test1.out

nosetests -v --with-xunit --xunit-file=regression_01.xml tests/test_regression.py

# generate regression XML
#lammps_generate_regression_xml --test-dir ${PWD}/tests/ --log-file test0.out --out-file regression_00.xml
#lammps_generate_regression_xml --test-dir ${PWD}/tests/ --log-file test1.out --out-file regression_01.xml

deactivate
