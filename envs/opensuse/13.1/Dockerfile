FROM opensuse:13.1

RUN zypper update -y
RUN zypper install -y gcc make cmake

RUN zypper install -y openmpi openmpi-devel
RUN zypper install -y mpich mpich-devel

RUN zypper install -y openssh

ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins

RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

RUN zypper install -y git

RUN zypper install -y ccache gcc-fortran fftw-devel libjpeg8-devel libjpeg-turbo libpng-devel python-devel blas-devel lapack-devel hdf5-devel

RUN zypper install -y -t pattern devel_rpm_build

RUN zypper install -y gcc-c++

USER jenkins

CMD /bin/bash
