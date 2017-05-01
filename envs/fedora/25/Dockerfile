FROM fedora:25

RUN dnf update -y && dnf groupinstall -y "Development tools"
RUN dnf install -y openmpi openmpi-devel
RUN dnf install -y clang
RUN dnf install -y mpich-devel
RUN dnf install -y openssh
RUN dnf install -y git
RUN dnf install -y ccache gcc-gfortran fftw-devel turbojpeg-devel libjpeg-turbo-devel libjpeg-turbo libpng-devel python-devel blas-devel lapack-devel hdf5-devel
RUN dnf install -y redhat-rpm-config
RUN dnf install -y @development-tools fedora-packager rpmdevtools
RUN dnf install -y valgrind
RUN dnf install -y wget

RUN wget https://github.com/michaelrsweet/htmldoc/releases/download/v1.8.30/htmldoc-1.8.30-source.tar.gz -O /tmp/htmldoc-1.8.30-source.tar.gz && mkdir /tmp/htmldoc-1.8.30 && cd /tmp/htmldoc-1.8.30 && tar xvzf /tmp/htmldoc-1.8.30-source.tar.gz && ./configure && make install && cd && rm -rf /tmp/htmldoc*

RUN dnf install -y python3 python-virtualenv python-nose python-pip
RUN dnf install -y which
RUN pip install --upgrade pip virtualenv
RUN pip install gcovr
RUN dnf update -y && dnf install -y texlive

ENV MODULEPATH /etc/modulefiles:/usr/share/modulefiles:/usr/share/Modules/modulefiles
ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins
RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

COPY z00_StdEnv.sh /etc/profile.d/z00_StdEnv.sh

USER jenkins

CMD /bin/bash
