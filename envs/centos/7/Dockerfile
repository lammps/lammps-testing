FROM centos:7

RUN yum update -y
RUN yum groupinstall -y "Development tools"
RUN yum install -y epel-release

RUN yum install -y \
    openmpi \
    openmpi-devel \
    clang \
    mpich-devel \
    openssh \
    git \
    wget \
    which \
    ccache \
    gcc-gfortran \
    fftw-devel \
    turbojpeg-devel \
    libjpeg-turbo-devel \
    libjpeg-turbo \
    libpng-devel \
    python-devel \
    blas-devel \
    lapack-devel \
    hdf5-devel \
    texlive \
    python36 \
    python36-virtualenv \
    python36-pip

RUN mkdir -p /tmp/htmldoc && \
    cd /tmp/htmldoc && \
    wget https://github.com/michaelrsweet/htmldoc/releases/download/v1.9.1/htmldoc-1.9.1-source.tar.gz && \
    tar xvzf htmldoc-1.9.1-source.tar.gz && \
    ./configure && \
    make install && \
    cd && \
    rm -rf /tmp/htmldoc

RUN pip3.6 install --upgrade pip virtualenv
RUN yum install -y cmake

ENV PATH /usr/lib/ccache:$PATH
ENV MODULEPATH /etc/modulefiles:/usr/share/modulefiles:/usr/share/Modules/modulefiles

COPY z00_StdEnv.sh /etc/profile.d/z00_StdEnv.sh

RUN groupadd -g 114 jenkins
RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

USER jenkins

CMD /bin/bash
