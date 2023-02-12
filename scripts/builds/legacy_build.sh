#!/bin/bash -x
if [ -z "${LAMMPS_DIR}" ]
then
    echo "Must set LAMMPS_DIR environment variable"
    exit 1
fi

if [ -z "${LAMMPS_CI_RUNNER}" ]
then
    # local testing
    BUILD=build-$(basename $0 .sh)
else
    # when running lammps_test or inside jenkins
    BUILD=build
fi

LAMMPS_COMPILE_NPROC=${LAMMPS_COMPILE_NPROC-8}

# static
# shared
if [ -z "$LAMMPS_MODE" ]
then
    export LAMMPS_MODE=static
fi

# SMALLSMALL
# SMALLBIG
# BIGBIG
if [ -z "$LAMMPS_SIZES" ]
then
    export LAMMPS_SIZES=SMALLBIG
fi

# CXX98
# CXX11
# CXX14
# CXX17
if [ -z "$LAMMPS_CXX_STANDARD" ]
then
    export LAMMPS_CXX_STANDARD=CXX11
fi

if [ -z "$LAMMPS_MACH" ]
then
    export LAMMPS_MACH=serial
fi

if [ -z "$LAMMPS_TARGET" ]
then
    export LAMMPS_TARGET=serial
fi

if [ -z "$LAMMPS_COMPILER" ]
then
    export LAMMPS_COMPILER=g++
fi

if [ -z "$CC" ]
then
    export CC=gcc
fi

if [ -z "$CXX" ]
then
    export CXX=g++
fi

enable_packages() {
    echo "Enable packages..."
    make -C ${LAMMPS_DIR}/src purge
    make -C ${LAMMPS_DIR}/src clean-all

    for PKG in "${LAMMPS_PACKAGES[@]}"
    do
        make -C ${LAMMPS_DIR}/src $PKG || exit 1
    done
}

build_libraries() {
    echo "Build libraries..."
    make -C ${LAMMPS_DIR}/src/STUBS clean

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-colvars"* ]]
    then
        make -C ${LAMMPS_DIR}/src lib-colvars args="-m ${LAMMPS_MACH}" CXX="${LAMMPS_COMPILER} -std=c++11"
    fi

#    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-colvars"* ]]
#    then
#        make -C ${LAMMPS_DIR}/lib/colvars -f Makefile.${LAMMPS_MACH} clean
#        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/colvars -f Makefile.${LAMMPS_MACH} CXX="${LAMMPS_COMPILER} -std=c++11" || exit 1
#    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-poems"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/poems -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/poems -f Makefile.${LAMMPS_MACH} CC="${LAMMPS_COMPILER} -std=c++11" LINK="${LAMMPS_COMPILER}" || exit 1
    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-awpmd"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/awpmd -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/awpmd -f Makefile.${LAMMPS_MACH} CC="${LAMMPS_COMPILER} -std=c++11" EXTRAMAKE=Makefile.lammps.installed || exit 1
    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-h5md"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/h5md -f Makefile.h5cc clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/h5md -f Makefile.h5cc || exit 1
    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-voronoi"* ]]
    then
        make -C ${LAMMPS_DIR}/src lib-voronoi args="-b" || exit 1
    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-atc"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/atc -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/atc -f Makefile.${LAMMPS_MACH} CC="${LAMMPS_COMPILER} -std=c++11" EXTRAMAKE="Makefile.lammps.installed" || exit 1
    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-qmmm"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/qmmm -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/qmmm -f Makefile.${LAMMPS_MACH} || exit 1
    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-machdyn"* ]]
    then
        make -C ${LAMMPS_DIR}/src lib-machdyn args="-p /usr/include/eigen3" || exit 1
    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-electrode"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/electrode -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/electrode -f Makefile.${LAMMPS_MACH} CC="${LAMMPS_COMPILER} -std=c++11" EXTRAMAKE=Makefile.lammps.installed || exit 1
    fi

    if [[ "${LAMMPS_PACKAGES[@]}" == *"yes-ml-pod"* ]] && [[ -d ${LAMMPS_DIR}/lib/mlpod ]]
    then
        make -C ${LAMMPS_DIR}/lib/mlpod -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/mlpod -f Makefile.${LAMMPS_MACH} CC="${LAMMPS_COMPILER} -std=c++11" EXTRAMAKE=Makefile.lammps.installed || exit 1
    fi
}

if [ -z "${CCACHE_DIR}" ]
then
    export CCACHE_DIR="$PWD/.ccache"
fi

export OMPI_CC=$CC
export OMPI_CXX=$CXX
export PYTHON=$(which python3)
export LMPFLAGS="-sf off"
export LMP_INC="-I/usr/include/hdf5/serial -DLAMMPS_${LAMMPS_SIZE} ${LAMMPS_EXCEPT} -DLAMMPS_${LAMMPS_CXX_STANDARD} -DFFT_KISSFFT -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized ${LAMMPS_TEST_COMPILE_FLAGS}"
export JPG_LIB="-L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -ljpeg -lpng -lz ${LAMMPS_TEST_LINK_FLAGS}"

# Configure
if [ "$LAMMPS_MACH" != 'mpi' ]
then
    export LMP_INC="-I../../src/STUBS ${LMP_INC}"
    export JPG_LIB="-L../../src/STUBS/ ${JPG_LIB} -lmpi_stubs"
fi

case $LAMMPS_CXX_STANDARD in
    CXX98)
        export LMP_INC="-std=c++98 ${LMP_INC}"
        ;;

    CXX11)
        export LMP_INC="-std=c++11 ${LMP_INC}"
        ;;

    CXX14)
        export LMP_INC="-std=c++14 ${LMP_INC}"
        ;;

    CXX17)
        export LMP_INC="-std=c++17 ${LMP_INC}"
        ;;
esac

ccache -M 10G

# Create copy of LAMMPS directory
echo "Copy sources..."

mkdir -p ${BUILD}/lammps
rsync -a --delete --include='src/***' --include='lib/***' --include='potentials/***' --include='python/***' --include='fmtlib/***' --exclude='*' ${LAMMPS_DIR}/ ${BUILD}/lammps/

export LAMMPS_DIR=${BUILD}/lammps

virtualenv --python=$PYTHON pyenv

source pyenv/bin/activate
pip install --upgrade pip setuptools

build_libraries

rm -f ${LAMMPS_DIR}/src/Makefile.package ${LAMMPS_DIR}/src/Makefile.package.settings

enable_packages

# Build
make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/src mode=${LAMMPS_MODE} ${LAMMPS_TARGET} MACH=${LAMMPS_MACH} CC="${LAMMPS_COMPILER}" LINK="${LAMMPS_COMPILER}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" CCFLAGS="${LAMMPS_FLAGS}" LINKFLAGS="${LAMMPS_FLAGS}" LMPFLAGS="${LMPFLAGS}" || exit 1

if [[ ("${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-python"*) ]]
then
    make -C ${LAMMPS_DIR}/src install-python || exit 1
fi

deactivate

ccache -s
