FROM fedora:24

RUN dnf update -y && dnf groupinstall -y "Development tools"

RUN dnf install -y openmpi openmpi-devel
RUN dnf install -y clang
RUN dnf install -y mpich-devel

ENV MODULEPATH /etc/modulefiles:/usr/share/modulefiles:/usr/share/Modules/modulefiles

COPY z00_StdEnv.sh /etc/profile.d/z00_StdEnv.sh

RUN dnf install -y openssh

ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins

RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

RUN dnf install -y git

RUN dnf install -y ccache gcc-gfortran fftw-devel turbojpeg-devel libjpeg-turbo-devel libjpeg-turbo libpng-devel python-devel blas-devel lapack-devel hdf5-devel

RUN dnf install -y redhat-rpm-config

RUN dnf install -y @development-tools fedora-packager rpmdevtools

RUN dnf install -y valgrind

RUN dnf install -y python-nose

RUN pip install gcovr

USER jenkins

CMD /bin/bash
