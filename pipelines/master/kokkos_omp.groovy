node {
    def build_name = 'jenkins/kokkos_omp'

    stage 'Checkout'
    git branch: 'master', credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps.git'
    sh 'cp src/MAKE/OPTIONS/Makefile.kokkos_omp src/MAKE/'

    //step([$class: 'GitHubCommitStatusSetter', contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'building...', state: 'PENDING']]]])

    env.CCACHE_DIR= pwd() + '/.ccache'
    env.COMP     = 'mpicxx'
    env.MACH     = 'kokkos_omp'
    env.LMP_INC  = '-I/usr/include/hdf5/serial -DFFT_KISSFFT -DLAMMPS_GZIP -DLAMMPS_PNG -DLAMMPS_JPEG -DLAMMPS_BIGBIG -Wall -Wextra -Wno-unused-result -Wno-unused-parameter -Wno-maybe-uninitialized'
    env.JPG_LIB  = '-L/usr/lib/x86_64-linux-gnu/hdf5/serial/ -ljpeg -lpng -lz'

    env.CC = 'gcc'
    env.CXX = 'g++'
    env.OMPI_CC = 'gcc'
    env.OMPI_CXX = 'g++'

    stage 'Setting up build environment'

    def envImage = docker.image('lammps_testing:ubuntu_latest')

    try {
        docker.withRegistry('http://glados.cst.temple.edu:5000') {
            // ensure image is current
            envImage.pull()

            // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
            docker.image(envImage.imageName()).inside {
                sh '${COMP} --version'
                sh 'ccache -C'
                sh 'ccache -M 5G'

                // clean up project directory
                sh '''
                make -C src purge
                make -C src clean-all
                make -C src yes-all
                make -C src no-lib
                make -C src no-user-omp
                make -C src no-user-intel
                make -C src no-user-smd
                '''

                stage 'Building libraries'

                sh '''
                make -C lib/colvars -f Makefile.g++ clean
                make -C lib/poems -f Makefile.g++ CXX="${COMP}" clean
                #make -C lib/voronoi -f Makefile.g++ CXX="${COMP}" clean
                make -C lib/awpmd -f Makefile.mpicc CC="${COMP}" clean
                make -C lib/h5md -f Makefile.h5cc clean

                make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
                make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
                #make -j 8 -C lib/voronoi -f Makefile.g++ CXX="${COMP}"
                make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
                make -j 8 -C lib/h5md -f Makefile.h5cc
                '''

                stage 'Enabling modules'

                sh '''
                #make -C src yes-user-smd yes-user-molfile yes-compress yes-python
                make -C src yes-user-molfile yes-compress yes-python

                #make -C src yes-poems yes-voronoi yes-user-colvars yes-user-awpmd yes-meam
                make -C src yes-poems yes-user-colvars yes-user-awpmd yes-user-meamc

                make -C src yes-user-h5md
                make -C src yes-mpiio yes-user-lb
                make -C src yes-kokkos
                '''

                stage 'Compiling'
                sh 'make -j 8 -C src ${MACH} CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC"'

                sh 'ccache -s'
            }
        }
        //step([$class: 'GitHubCommitStatusSetter', contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'build successful!', state: 'SUCCESS']]]])
    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
        //step([$class: 'GitHubCommitStatusSetter', contextSource: [$class: 'ManuallyEnteredCommitContextSource', context: build_name], statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'build failed!', state: 'FAILURE']]]])
    }

    step([$class: 'WarningsPublisher', canComputeNew: false, consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']], defaultEncoding: '', excludePattern: '', healthy: '', includePattern: '', messagesPattern: '', unHealthy: ''])
    step([$class: 'AnalysisPublisher', canComputeNew: false, defaultEncoding: '', healthy: '', unHealthy: ''])

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
