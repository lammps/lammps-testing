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
export COVERAGE_RCFILE=$SCRIPTDIR/.coveragerc

cd ${BUILD}

echo "Running tests in parallel with CTEST_PARALLEL_LEVEL=$CTEST_PARALLEL_LEVEL"
ctest -V --no-compress-output -T Test

make gen_coverage_xml
make gen_python_coverage_xml || true

deactivate
