#!/bin/bash
# exe
# shexe
# shlib
if [ -z "$LAMMPS_MODE" ]
then
    export LAMMPS_MODE=exe
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

if [ -z "$LAMMPS_PACKAGES_ARRAY" ]
then
    IFS=':' read -a LAMMPS_PACKAGES_ARRAY <<< "${LAMMPS_PACKAGES}"
fi


enable_packages() {
    echo "Enable packages..."
    make -C ${LAMMPS_DIR}/src purge
    make -C ${LAMMPS_DIR}/src clean-all

    for PKG in "${LAMMPS_PACKAGES_ARRAY[@]}"
    do
        make -C ${LAMMPS_DIR}/src $PKG
    done
}

build_libraries() {
    echo "Build libraries..."
    make -C ${LAMMPS_DIR}/src/STUBS clean

    if [[ "${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-user-colvars"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/colvars -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/colvars -f Makefile.${LAMMPS_MACH} CXX="${LAMMPS_COMPILER} -std=c++11"
    fi

    if [[ "${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-poems"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/poems -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/poems -f Makefile.${LAMMPS_MACH} CC="${LAMMPS_COMPILER}" LINK="${LAMMPS_COMPILER}"
    fi

    if [[ "${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-user-awpmd"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/awpmd -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/awpmd -f Makefile.${LAMMPS_MACH} CC="${LAMMPS_COMPILER}" EXTRAMAKE=Makefile.lammps.installed
    fi

    if [[ "${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-user-h5md"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/h5md -f Makefile.h5cc clean
        make -j 8 -C ${LAMMPS_DIR}/lib/h5md -f Makefile.h5cc
    fi

    if [[ "${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-voronoi"* ]]
    then
        make -C ${LAMMPS_DIR}/src lib-voronoi args="-b"
    fi

    if [[ "${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-user-atc"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/atc -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/atc -f Makefile.${LAMMPS_MACH} EXTRAMAKE="Makefile.lammps.installed"
    fi

    if [[ "${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-user-qmmm"* ]]
    then
        make -C ${LAMMPS_DIR}/lib/qmmm -f Makefile.${LAMMPS_MACH} clean
        make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/lib/qmmm -f Makefile.${LAMMPS_MACH}
    fi

    if [[ "${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-user-smd"* ]]
    then
        make -C ${LAMMPS_DIR}/src lib-smd args="-p /usr/include/eigen3"
    fi
}

export CCACHE_DIR="$PWD/.ccache"
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

ccache -M 5G

# Create copy of LAMMPS directory
echo "Copy sources..."

git -C ${LAMMPS_DIR} rev-parse HEAD > COMMIT

rsync -a --include='src/***' --include='lib/***' --include='potentials/***' --include='python/***' --exclude='*' ${LAMMPS_DIR}/ .

export LAMMPS_DIR=$PWD

virtualenv --python=$PYTHON pyenv

source pyenv/bin/activate

enable_packages

# Build
build_libraries
#
touch ${LAMMPS_DIR}/src/liblammps.so
make -j ${LAMMPS_COMPILE_NPROC} -C ${LAMMPS_DIR}/src mode=${LAMMPS_MODE} ${LAMMPS_TARGET} MACH=${LAMMPS_MACH} CC="${LAMMPS_COMPILER}" LINK="${LAMMPS_COMPILER}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" LMPFLAGS="${LMPFLAGS}"

if [[ ("${LAMMPS_PACKAGES_ARRAY[@]}" == *"yes-python"*) ]]
then
    make -C ${LAMMPS_DIR}/src install-python
fi

# equivalent of make install --prefix=$VIRTUAL_ENV, but avoid copies
# library should already be installed at right place by install-python
mkdir -p ${VIRTUAL_ENV}/bin
mkdir -p ${VIRTUAL_ENV}/share/lammps
ln -s ${LAMMPS_DIR}/src/lmp_${LAMMPS_MACH} ${VIRTUAL_ENV}/bin/lmp
ln -s $PWD/potentials ${VIRTUAL_ENV}/share/lammps/potentials

deactivate

ccache -s

export LAMMPS_BUILD_DIR=$PWD
