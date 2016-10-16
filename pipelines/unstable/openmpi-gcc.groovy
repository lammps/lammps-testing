node {
    def build_name = 'jenkins/openmpi-gcc'

    env.CCACHE_DIR= pwd() + '/.ccache'
    env.COMP     = 'mpicxx'
    env.MACH     = 'mpi'
    env.MPICMD   = 'mpirun -np 4'
    env.LMPFLAGS = '-sf off'
    env.LMP_INC  = '-I/usr/include/hdf5/serial -DFFT_KISSFFT -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -DLAMMPS_BIGBIG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized'
    env.JPG_LIB  = '-L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -ljpeg -lpng -lz'

    env.CC = 'gcc'
    env.CXX = 'g++'
    env.OMPI_CC = 'gcc'
    env.OMPI_CXX = 'g++'

    env.LAMMPS_DIR = pwd()
    env.LAMMPS_MPI_MODE = 'openmpi'
    env.LAMMPS_BINARY = pwd() + '/src/lmp_' + env.MACH
    env.LAMMPS_TEST_MODES = 'serial:parallel'


    stage('Checkout'){
        git branch: 'unstable', credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps.git'

        dir('lammps-testing') {
            git url: 'https://github.com/lammps/lammps-testing.git', credentialsId: 'lammps-jenkins', branch: 'master'
        }
    }
    


    try {
        docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
            stage('Setting up build environment') {
                def envImage = docker.image('rbberger/lammps-testing:ubuntu_latest')

                // ensure image is current
                envImage.pull()
            }

            // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
            docker.image(envImage.imageName()).inside {
                sh 'ccache -C'
                sh 'ccache -M 5G'

                if (! fileExists('pyenv') ) {
                    sh 'virtualenv pyenv'
                }

                sh '''
                source pyenv/bin/activate
                pip install nose
                pip install nose2
                deactivate
                '''

                // clean up project directory
                sh '''
                make -C src clean-all
                make -C src yes-all
                make -C src no-lib
                make -C src no-user-omp
                make -C src no-user-intel
                make -C src no-user-smd
                '''

                stage('Building libraries') {
                    sh '''
                    make -C lib/colvars -f Makefile.g++ clean
                    make -C lib/poems -f Makefile.g++ CXX="${COMP}" clean
                    make -C lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
                    make -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran clean
                    make -C lib/h5md clean

                    make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
                    make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
                    make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
                    make -j 8 -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran
                    make -j 8 -C lib/h5md
                    '''

                    sh '''
                    cd lib/voronoi
                    rm -rf build
                    python2 install.py -d build -g
                    sed -i 's/CFLAGS=/CFLAGS=-fPIC /' build/voro++-0.4.6/config.mk
                    python2 install.py -d build -b -l
                    '''
                }

                stage('Enabling modules') {
                    sh '''
                    make -C src yes-user-molfile yes-compress yes-python

                    make -C src yes-poems yes-voronoi yes-user-colvars yes-user-awpmd yes-meam
                    make -C src yes-user-h5md
                    make -C src yes-mpiio yes-user-lb
                    '''
                }

                stage('Compiling') {
                    sh 'make -j 8 -C src mode=shexe ${MACH} MPICMD="${MPICMD}" CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC" LMPFLAGS="${LMPFLAGS}"'
                }

                stage('Testing') {
                    sh '''
                    source pyenv/bin/activate
                    cd python
                    python install.py
                    cd ..
                    cd lammps-testing
                    env
                    python run_tests.py --processes 8 tests/test_commands.py tests/test_examples.py
                    cd ..
                    deactivate
                    '''
                }

                sh 'ccache -s'
            }
        }
    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
    }

    step([$class: 'WarningsPublisher', canComputeNew: false, consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']], defaultEncoding: '', excludePattern: '', healthy: '', includePattern: '', messagesPattern: '', unHealthy: ''])
    step([$class: 'AnalysisPublisher', canComputeNew: false, defaultEncoding: '', healthy: '', unHealthy: ''])
    junit 'lammps-testing/nosetests-*.xml'
}
