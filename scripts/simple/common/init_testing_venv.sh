#!/bin/bash
echo "Setting up virtual environment with lammps-testing installed..."

if [ -z "${LAMMPS_TESTING_DIR}" ]
then
    echo "Must set LAMMPS_TESTING_DIR environment variable"
    exit 1
fi

if [ -z "${PYTHON}" ]
then
    echo "Must set PYTHON environment variable"
    exit 1
fi

if [ -d "pyenv" ]
then
    rm -rf pyenv
fi

virtualenv --python=$PYTHON pyenv
source pyenv/bin/activate
pip install --upgrade pip setuptools

# avoid multiple parallel jobs writing in the same temporary directories
PYTHON_BUILD_DIR=$PWD/python_build

if [ -d "$PYTHON_BUILD_DIR" ]; then
    rm -rf $PYTHON_BUILD_DIR
fi

mkdir -p $PYTHON_BUILD_DIR

# install lammps-testing package
cd $LAMMPS_TESTING_DIR

python setup.py build --build-base $PYTHON_BUILD_DIR/build \
                egg_info --egg-base $PYTHON_BUILD_DIR \
                bdist_egg --dist-dir $PYTHON_BUILD_DIR/dist \
                install || exit 1
