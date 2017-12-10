FROM opensuse:42.3

RUN zypper update -y
RUN zypper install -y gcc clang make cmake
RUN zypper install -y openmpi openmpi-devel
RUN zypper install -y openssh
RUN zypper install -y git
RUN zypper install -y ccache gcc-fortran fftw-devel libjpeg8-devel libjpeg-turbo libpng-devel python-devel blas-devel lapack-devel hdf5-devel
RUN zypper install -y -t pattern devel_rpm_build
RUN zypper install -y gcc-c++
RUN zypper install -y valgrind
RUN zypper install -y wget
RUN zypper install -y rpm-build

RUN mkdir -p /tmp/htmldoc && cd /tmp/htmldoc && wget https://github.com/michaelrsweet/htmldoc/releases/download/v1.9.1/htmldoc-1.9.1-source.tar.gz && tar xvzf htmldoc-1.9.1-source.tar.gz && ./configure && make install && cd && rm -rf /tmp/htmldoc

RUN zypper install -y python3 python-virtualenv python-nose python-pip
RUN zypper install -y which
RUN pip install --upgrade pip virtualenv
RUN pip install gcovr
RUN zypper install -y texlive texlive-scheme-medium

ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins
RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

USER jenkins

CMD /bin/bash
