FROM nvidia/cuda:10.2-devel-ubuntu18.04

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV DEBIAN_FRONTEND noninteractive

RUN groupadd -g 114 jenkins
RUN useradd -u 108 -g 114 -ms /bin/bash jenkins

RUN apt update && apt upgrade -y && apt install -y build-essential ccache gfortran openmpi-bin libopenmpi-dev libfftw3-dev libjpeg-dev libpng-dev python-dev python3-dev libblas-dev liblapack-dev libhdf5-serial-dev hdf5-tools clang git dh-make bzr-builddeb htmldoc gcc g++ python-virtualenv texlive bc cmake libvtk6-dev libeigen3-dev ssh libproj-dev texlive-latex-extra python-pygments


#install latest cmake
ADD https://cmake.org/files/v3.12/cmake-3.12.0-Linux-x86_64.sh /cmake-3.12.0-Linux-x86_64.sh
RUN mkdir /opt/cmake
RUN sh /cmake-3.12.0-Linux-x86_64.sh --prefix=/opt/cmake --skip-license
RUN ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake
RUN cmake --version

COPY openmpi-mca-params.conf /etc/openmpi/openmpi-mca-params.conf
RUN apt install --no-install-recommends -y ocl-icd-opencl-dev ocl-icd-libopencl1 clinfo
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

RUN apt install -y vim
RUN apt install -y gdb
RUN apt install -y valgrind
RUN apt-get update -y && apt-get -y install libenchant-dev
RUN apt-get update -y && apt-get -y install libgsl0-dev gsl-bin
RUN apt-get update -y && apt-get -y install xxd
RUN apt-get update -y && apt-get -y install ninja-build
RUN apt-get update -y && apt-get -y install rsync

ENV PATH /usr/lib/ccache:$PATH

USER jenkins

CMD /bin/bash
