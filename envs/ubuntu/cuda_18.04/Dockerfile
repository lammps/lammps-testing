FROM nvidia/cuda:9.2-devel-ubuntu18.04

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:ubuntu-toolchain-r/test && apt-get update && apt-get upgrade -y

RUN groupadd -g 114 jenkins
RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

RUN apt install -y build-essential ccache gfortran openmpi-bin libopenmpi-dev libfftw3-dev libjpeg-dev libpng-dev python-dev libblas-dev liblapack-dev libhdf5-serial-dev hdf5-tools clang git dh-make bzr-builddeb htmldoc gcc-6 g++-6 python-virtualenv texlive bc gfortran-6 cmake libvtk6-dev libeigen3-dev ssh libproj-dev

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

ENV PATH /usr/lib/ccache:$PATH

USER jenkins

CMD /bin/bash
