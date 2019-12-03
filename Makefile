# Requires LAMMPS_DIR and LAMMPS_COMPILE_NPROC env variables to be set
 
.PHONY: containers ubuntu_serial ubuntu_cmake_serial

SCRIPTSDIR=${CURDIR}/scripts

UBUNTU_CONTAINER=build/containers/ubuntu_18.04.sif

containers: ${UBUNTU_CONTAINER}

build/containers/%.sif: containers/singularity/%.def
	mkdir -p build/containers
	sudo singularity build $@ $<

ubuntu_serial: ${UBUNTU_CONTAINER}
	-rm -rf build/ubuntu_serial
	mkdir -p build/ubuntu_serial
	cd build/ubuntu_serial && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/Serial.sh

ubuntu_cmake_serial: ${UBUNTU_CONTAINER}
	-rm -rf build/cmake_serial
	mkdir build/cmake_serial
	cd build/cmake_serial && singularity run -B ${LAMMPS_DIR}:${LAMMPS_DIR} -B ${SCRIPTSDIR}/:${SCRIPTSDIR}/ ../../${UBUNTU_CONTAINER} ${SCRIPTSDIR}/CMakeSerial.sh
