# LAMMPS Test Suite

This repository contains code and examples that drive the regression testing on
[ci.lammps.org](https://ci.lammps.org). It's is run on hardware that is hosted
at Temple University.

The tools provided here can also be installed locally for testing on a workstation.

## Installation

```bash
python setup.py install
```

## Configuration

```bash
export LAMMPS_DIR=$HOME/GitHub/lammps/lammps
export LAMMPS_TESTING_DIR=$HOME/GitHub/lammps/lammps-testing
export LAMMPS_CACHE_DIR=$HOME/GitHub/lammps/lammps-testing/build
export LAMMPS_COMPILE_NPROC=24
```

`LAMMPS_DIR`
LAMMPS source directory

`LAMMPS_TESTING_DIR`
LAMMPS testing source directory

`LAMMPS_CACHE_DIR`
Directory storing compiled binaries and containers

## Overview

`lammps_test` is a utility to build LAMMPS in different configurations with
both Make and CMake on various containerized platforms and perform both runtime
tests and regression testing.

It does so by maintaining directory structure of builds based on the current
Git checkout of LAMMPS located in `LAMMPS_DIR`.

To see the currently available environments and configurations, as well as
their build status, use the `lammps_test status` command:

```bash
lammps_test status
````

## Build environments

To make builds reproducable, `lammps_test` uses Singularity containers for
building all binaries. Singularity must be installed and the current user must
have sudo rights to build containers.

Before any compilations can happen you need to create the necessary container.

```bash
# build default environment
lammps_test buildenv

# build NVIDIA build environment
lammps_test --env=ubuntu_18.04_nvidia buildenv
```

## LAMMPS Configurations

Configurations define what features should be enabled in a LAMMPS build. They
are defined by YAML files stored in the `configurations` folder. The following is a
simple configuration file.

```yaml
---
mpi: no
openmp: no
compiler: g++
cc: gcc
cxx: g++
sizes: smallsmall
exceptions: no
packages:
 - MOLECULE
```

If this file is called `configurations/simple.yml`,
you can select this configuration as `simple` inside of `lammps_test`.

## Building LAMMPS

To build LAMMPS using a configuration in an environment you can use the `lammps_test build` command.
It is followed by one ore more configuration names. You can also build all configurations using `ALL`

During a build, `lammps_test` will perform an out-of-source build of LAMMPS
based on the current commit of the LAMMPS Git repository located in
`LAMMPS_DIR`. This build will be located in a subdirectory of
`LAMMPS_CACHE_DIR`.

```bash
# build LAMMPS with simple configuration
lammps_test build simple

# build LAMMPS with serial configuration
lammps_test build serial

# build LAMMPS with serial and openmpi configuration
lammps_test build serial openmpi

# build LAMMPS in all configurations
lammps_test build ALL
```

Once completed, you can always verify the current state of your testing system using `lammps_test status`

## LAMMPS Builders

`lammps_test` allows you to choose between two builders: `legacy` and `cmake`.
By default it uses the `legacy` builder, which uses the original Makefiles of
LAMMPS. Each builder uses the LAMMPS configuration specified by the YAML file
and transforms it into the appropiate commands to create the specified build.

```bash
# build LAMMPS with serial configuration using CMake
lammps_test build --builder=cmake serial

# build LAMMPS with serial configuration using Legacy Make
lammps_test build --builder=legacy serial
```

If you want to build in a different environment, add the `--env` option before
the `build` command:

```bash
#################################################################
# using the NVIDIA environment
##################################################################

# build LAMMPS with 'testing_gpu_cuda' configuration using CMake
lammps_test --env=ubuntu_18.04_nvidia build --builder=cmake testing_gpu_cuda

# build LAMMPS with 'testing_gpu_cuda' configuration using Legacy Make
lammps_test --env=ubuntu_18.04_nvidia build --builder=legacy testing_gpu_cuda
```

## Running LAMMPS

```bash
lammps_test run "-in in.melt"
lammps_test --env=ubuntu_18.04_nvidia run --builder=cmake --config=testing_gpu_cuda "-in in.melt"
```

## Running LAMMPS run tests

```bash
lammps_test runtests commands
lammps_test runtests examples
```

## Running LAMMPS regression testing

```bash
lammps_test regression --builder=cmake --config=regression tests/examples/granregion/in.granregion.box
```
