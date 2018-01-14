FROM ubuntu:16.04

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y software-properties-common python-software-properties
RUN add-apt-repository ppa:ubuntu-toolchain-r/test && apt-get update && apt-get upgrade -y

RUN groupadd -g 114 jenkins
RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

RUN apt install -y build-essential ccache gfortran openmpi-bin libopenmpi-dev libfftw3-dev libjpeg-dev libpng12-dev python-dev libblas-dev liblapack-dev libhdf5-serial-dev hdf5-tools clang git dh-make bzr-builddeb htmldoc gcc-6 g++-6 python-virtualenv texlive bc gfortran-6 cmake libvtk6-dev libeigen3-dev ssh libproj-dev

ENV PATH /usr/lib/ccache:$PATH

#USER jenkins

CMD /bin/bash
