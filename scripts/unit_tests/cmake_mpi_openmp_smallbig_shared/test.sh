#!/bin/bash
export WORKING_DIR=$PWD
SCRIPTDIR="$(dirname "$(realpath "$0")")"

if [ -z "${LAMMPS_CI_RUNNER}" ]
then
    # local testing
    BUILD=build-$(basename $0 .sh)
else
    # when running lammps_test or inside jenkins
    BUILD=build
fi

source pyenv/bin/activate
export LC_ALL=C.UTF-8

cd ${BUILD}

export CTEST_PARALLEL_LEVEL=$LAMMPS_COMPILE_NPROC
ctest -V --no-compress-output -T Test

make gen_coverage_xml

deactivate
