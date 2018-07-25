FROM ubuntu:18.04

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV DEBIAN_FRONTEND noninteractive

RUN groupadd -g 114 jenkins
RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

RUN apt update && apt upgrade -y && apt install -y build-essential ccache gfortran openmpi-bin libopenmpi-dev libfftw3-dev libjpeg-dev libpng-dev python-dev libblas-dev liblapack-dev libhdf5-serial-dev hdf5-tools clang git dh-make bzr-builddeb htmldoc gcc g++ python-virtualenv texlive bc cmake libvtk6-dev libeigen3-dev ssh libproj-dev

ENV PATH /usr/lib/ccache:$PATH

USER jenkins

CMD /bin/bash
