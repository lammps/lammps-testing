FROM ubuntu:16.04

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV DEBIAN_FRONTEND noninteractive

RUN apt update && apt install -y build-essential ccache gfortran openmpi-bin libopenmpi-dev  libfftw3-dev libjpeg-dev libpng12-dev python-dev libblas-dev liblapack-dev libhdf5-serial-dev hdf5-tools clang

RUN apt install -y ssh

ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins

RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

RUN apt install -y git

RUN apt install -y dh-make bzr-builddeb

RUN apt-get update && apt-get install -y htmldoc

RUN apt-get update && apt-get install -y python-virtualenv

USER jenkins

CMD /bin/bash
