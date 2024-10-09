#!/bin/bash
echo "Setting up virtual environment with lammps-testing installed..."

if [ -z "${LAMMPS_TESTING_DIR}" ]
then
    echo "Must set LAMMPS_TESTING_DIR environment variable"
    exit 1
fi

source pyenv/bin/activate

pip install --upgrade pip setuptools wheel build

# avoid multiple parallel jobs writing in the same temporary directories
PYTHON_BUILD_DIR=$PWD/python_${BUILD}

if [ -d "$PYTHON_BUILD_DIR" ]; then
    rm -rf $PYTHON_BUILD_DIR
fi

mkdir -p $PYTHON_BUILD_DIR

# install lammps-testing package
cd $LAMMPS_TESTING_DIR

# modern way of building the wheel
python -m build -w -v --outdir $PYTHON_BUILD_DIR
pip install $PYTHON_BUILD_DIR/lammps_testing-*.whl

deactivate
