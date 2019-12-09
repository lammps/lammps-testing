#!/bin/bash

. $SCRIPTDIR/LAMMPSTesting.sh

source $LAMMPS_BUILD_DIR/pyenv/bin/activate
lammps_run_tests --processes 8 tests/test_commands.py tests/test_examples.py

#cd ${LAMMPS_BUILD_DIR}
#make gen_coverage_xml

deactivate
