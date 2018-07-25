FROM centos:6

RUN yum update -y && yum groupinstall -y "Development tools"

RUN yum install -y openmpi openmpi-devel
RUN yum install -y mpich-devel

ENV MODULEPATH /etc/modulefiles:/usr/share/modulefiles:/usr/share/Modules/modulefiles

COPY z00_StdEnv.sh /etc/profile.d/z00_StdEnv.sh
COPY texlive.profile /etc/texlive.profile

RUN yum install -y openssh

ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins

RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

RUN yum install -y git

RUN yum install -y ccache gcc-gfortran fftw-devel turbojpeg-devel libjpeg-turbo-devel libjpeg-turbo libpng-devel python-devel blas-devel lapack-devel hdf5-devel

RUN yum install -y redhat-rpm-config

RUN yum install -y @development-tools fedora-packager rpmdevtools

RUN yum install -y wget

RUN mkdir -p /tmp/htmldoc && cd /tmp/htmldoc && wget https://github.com/michaelrsweet/htmldoc/releases/download/v1.9.1/htmldoc-1.9.1-source.tar.gz && tar xvzf htmldoc-1.9.1-source.tar.gz && ./configure && make install && cd && rm -rf /tmp/htmldoc

RUN yum install -y which

RUN yum install -y https://centos6.iuscommunity.org/ius-release.rpm
RUN yum install -y python35u python35u-pip
RUN pip3.5 install virtualenv

RUN wget http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz -O /tmp/install-tl-unx.tar.gz && cd /tmp && tar xvzf /tmp/install-tl-unx.tar.gz && cd install-tl-* && ./install-tl --profile=/etc/texlive.profile && cd && rm -rf /tmp/install-tl-*

RUN ln -s /usr/bin/python3.5 /usr/bin/python3

USER jenkins

CMD /bin/bash
