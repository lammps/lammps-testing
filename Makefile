# Requires LAMMPS_DIR and LAMMPS_COMPILE_NPROC env variables to be set
 
.PHONY: containers ubuntu_documentation ubuntu_serial ubuntu_shlib ubuntu_openmpi ubuntu_serial_clang ubuntu_shlib_clang ubuntu_openmpi_clang ubuntu_cmake_serial ubuntu_cmake_testing all

SCRIPTSDIR=${CURDIR}/scripts

UBUNTU_CONTAINER=build/containers/ubuntu_18.04.sif

containers: ${UBUNTU_CONTAINER}

build/containers/%.sif: containers/singularity/%.def
	mkdir -p build/containers
	sudo singularity build $@ $<

ubuntu_documentation: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/Documentation.sh

ubuntu_serial: ${ubuntu_container}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/Serial.sh

ubuntu_regression_build: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/RegressionBuild.sh

build/ubuntu_regression_build/pyenv/bin/lmp: ubuntu_regression_build

ubuntu_run_regression_tests: export LAMMPS_BUILD_DIR=${PWD}/build/ubuntu_regression_build

ubuntu_run_regression_tests: ${UBUNTU_CONTAINER} build/ubuntu_regression_build/pyenv/bin/lmp
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${LAMMPS_BUILD_DIR}:${LAMMPS_BUILD_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/RunRegressionTests.sh

ubuntu_serial_clang: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/SerialClang.sh

ubuntu_shlib: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/Shlib.sh

ubuntu_shlib_clang: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/ShlibClang.sh

ubuntu_openmpi: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/OpenMPI.sh

ubuntu_openmpi_clang: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/OpenMPIClang.sh

ubuntu_cmake_serial: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/CMakeSerial.sh

ubuntu_cmake_testing: ${UBUNTU_CONTAINER}
	mkdir -p build/$@
	cd build/$@ && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/CMakeSerialTesting.sh

all: ubuntu_documentation ubuntu_serial ubuntu_serial_clang ubuntu_shlib ubuntu_shlib_clang ubuntu_openmpi ubuntu_openmpi_clang ubuntu_cmake_serial
