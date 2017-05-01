FROM fedora:21

RUN yum update -y && yum groupinstall -y "Development tools"
RUN yum install -y openmpi openmpi-devel
RUN yum install -y clang
RUN yum install -y mpich-devel
RUN yum install -y openssh
RUN yum install -y git
RUN yum install -y ccache gcc-gfortran fftw-devel turbojpeg-devel libjpeg-turbo-devel libjpeg-turbo libpng-devel python-devel blas-devel lapack-devel hdf5-devel

RUN yum install -y redhat-rpm-config
RUN yum install -y @development-tools fedora-packager rpmdevtools
RUN yum install -y valgrind
RUN yum install -y wget
RUN yum install -y gcc-c++

RUN wget https://github.com/michaelrsweet/htmldoc/releases/download/v1.8.30/htmldoc-1.8.30-source.tar.gz -O /tmp/htmldoc-1.8.30-source.tar.gz && mkdir /tmp/htmldoc-1.8.30 && cd /tmp/htmldoc-1.8.30 && tar xvzf /tmp/htmldoc-1.8.30-source.tar.gz && ./configure && make install && cd && rm -rf /tmp/htmldoc*

RUN yum install -y python3 python-virtualenv python-nose python-pip
RUN yum install -y which
RUN pip install --upgrade pip virtualenv
RUN pip install gcovr
RUN yum update -y && yum install -y texlive

ENV MODULEPATH /etc/modulefiles:/usr/share/modulefiles:/usr/share/Modules/modulefiles
ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins
RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

COPY z00_StdEnv.sh /etc/profile.d/z00_StdEnv.sh

USER jenkins

CMD /bin/bash
