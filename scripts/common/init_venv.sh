#!/bin/bash
echo "Setting up Python virtual environment..."

if [ -z "${PYTHON}" ]
then
    echo "Must set PYTHON environment variable"
    exit 1
fi

if [ -d "pyenv" ]
then
    rm -rf pyenv
fi

PYTHON_MAJOR_VERSION=`${PYTHON} --version | awk '{print $2}' | cut -d. -f1`

if [ $PYTHON_MAJOR_VERSION -eq 2 ]
then
    virtualenv --python=$PYTHON pyenv
else
    ${PYTHON} -m venv pyenv
fi

source pyenv/bin/activate

pip install --upgrade pip setuptools wheel

deactivate
