FROM fedora:20

RUN yum update -y && yum groupinstall -y "Development tools"

RUN yum install -y openmpi openmpi-devel
RUN yum install -y clang
RUN yum install -y mpich-devel

ENV PATH             /usr/lib64/openmpi/bin:$PATH
ENV LD_LIBRARY_PATH  /usr/lib64/openmpi/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH       /usr/lib64/python2.7/site-packages/openmpi:$PYTHONPATH
ENV MANPATH          /usr/share/man/openmpi-x86_64:$MANPATH

ENV MPI_BIN             /usr/lib64/openmpi/bin
ENV MPI_SYSCONFIG       /etc/openmpi-x86_64
ENV MPI_FORTRAN_MOD_DIR /usr/lib64/gfortran/modules/openmpi-x86_64
ENV MPI_INCLUDE         /usr/include/openmpi-x86_64
ENV MPI_LIB             /usr/lib64/openmpi/lib
ENV MPI_MAN             /usr/share/man/openmpi-x86_64
ENV MPI_PYTHON_SITEARCH /usr/lib64/python2.7/site-packages/openmpi
ENV MPI_COMPILER        openmpi-x86_64
ENV MPI_SUFFIX          _openmpi
ENV MPI_HOME            /usr/lib64/openmpi


RUN yum install -y openssh

ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins

RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

RUN yum install -y git

RUN yum install -y ccache gcc-gfortran fftw-devel turbojpeg-devel libjpeg-turbo-devel libjpeg-turbo libpng-devel python-devel blas-devel lapack-devel hdf5-devel

RUN yum install -y redhat-rpm-config

RUN yum install -y @development-tools fedora-packager rpmdevtools

RUN yum install -y gcc-c++

USER jenkins

CMD /bin/bash
