#!/bin/bash

# Create copy of LAMMPS directory
echo "Copy sources..."
rsync -a --include='doc/***' --include='src/***' --include='python/***' --exclude='*' ${LAMMPS_DIR}/ .

export LAMMPS_DIR=$PWD

make -C ${LAMMPS_DIR}/doc clean-all

# Generate HTML
make -C ${LAMMPS_DIR}/doc -j ${LAMMPS_COMPILE_NPROC} html

# Generate PDF
make -C ${LAMMPS_DIR}/doc pdf

# Check Spelling
make -C ${LAMMPS_DIR}/doc -j ${LAMMPS_COMPILE_NPROC} spelling
