FROM fedora:29

RUN dnf update -y
RUN dnf install -y make python3 python3-virtualenv python3-nose python3-pip ccache git patch dos2unix openssh which wget Lmod texlive cmake gcc
RUN dnf install -y mingw32-nsis mingw32-gcc-c++ mingw32-gcc-gfortran mingw32-libjpeg-turbo-static mingw32-libpng-static mingw32-zlib-static mingw32-libgomp mingw32-winpthreads-static
RUN dnf install -y mingw64-gcc-c++ mingw64-gcc-gfortran mingw64-libjpeg-turbo-static mingw64-libpng-static mingw64-zlib-static mingw64-libgomp mingw64-winpthreads-static

RUN pip3 install --upgrade pip virtualenv

RUN mkdir -p /tmp/dl && cd /tmp/dl && wget https://download.lammps.org/thirdparty/opencl-win-devel.tar.gz && tar -xzvf opencl-win-devel.tar.gz && cp -ar OpenCL/include/CL /usr/i686-w64-mingw32/sys-root/mingw/include/  && cp -ar OpenCL/include/CL /usr/x86_64-w64-mingw32/sys-root/mingw/include/ && cp OpenCL/lib_win32/libOpenCL.dll /usr/i686-w64-mingw32/sys-root/mingw/lib  && cp OpenCL/lib_win64/libOpenCL.dll /usr/x86_64-w64-mingw32/sys-root/mingw/lib && cd && rm -rf /tmp/dl

ENV MODULEPATH /etc/modulefiles:/usr/share/modulefiles:/usr/share/Modules/modulefiles
ENV PATH /usr/lib/ccache:$PATH

RUN groupadd -g 114 jenkins
RUN useradd -u 106 -g 114 -ms /bin/bash jenkins

COPY z00_StdEnv.sh /etc/profile.d/z00_StdEnv.sh

USER jenkins

CMD /bin/bash
