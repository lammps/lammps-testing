node {
   def build_name = 'jenkins/openmpi-pr'
   def merge_branch = 'origin-pull/pull/' + env.GITHUB_PR_NUMBER + '/merge'
   def merge_refspec = '+refs/pull/' + env.GITHUB_PR_NUMBER + '/merge:refs/remotes/origin-pull/pull/' + env.GITHUB_PR_NUMBER +'/merge'

   stage 'Checkout'
   checkout([$class: 'GitSCM', branches: [[name: merge_branch]], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', name: 'origin-pull', refspec: merge_refspec, url: 'https://github.com/lammps/lammps-git-tutorial']]])
   git_commit = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

   step([$class: 'GitHubPRStatusBuilder', statusMessage: [content: env.GITHUB_PR_COND_REF + ' run started']])

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

    stage 'Setting up build environment'

    def envImage = docker.image('rbberger/lammps-testing:ubuntu_latest')

    try {
        docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
            // ensure image is current
            envImage.pull()

            // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
            docker.image(envImage.imageName()).inside {
                sh 'ccache -C'
                sh 'ccache -M 5G'

                // clean up project directory
                sh '''
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
                make -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran clean
                make -C lib/h5md -f Makefile.h5cc clean

                make -j 8 -C lib/colvars -f Makefile.g++ CXX="${COMP}"
                make -j 8 -C lib/poems -f Makefile.g++ CXX="${COMP}"
                #make -j 8 -C lib/voronoi -f Makefile.g++ CXX="${COMP}"
                make -j 8 -C lib/awpmd -f Makefile.mpicc CC="${COMP}"
                make -j 8 -C lib/meam -f Makefile.gfortran CC=gcc F90=gfortran
                make -j 8 -C lib/h5md -f Makefile.h5cc
                '''

                stage 'Enabling modules'

                sh '''
                #make -C src yes-user-smd yes-user-molfile yes-compress yes-python
                make -C src yes-user-molfile yes-compress yes-python

                #make -C src yes-poems yes-voronoi yes-user-colvars yes-user-awpmd yes-meam
                make -C src yes-poems yes-user-colvars yes-user-awpmd yes-meam

                make -C src yes-user-h5md
                make -C src yes-mpiio yes-user-lb
                '''

                stage 'Compiling'
                sh 'make -j 8 -C src ${MACH} MPICMD="${MPICMD}" CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC" LMPFLAGS="${LMPFLAGS}"'

                //stage 'Testing'
                //sh 'make -C src test-${MACH} MPICMD="${MPICMD}" CC="${COMP}" LINK="${COMP}" LMP_INC="${LMP_INC}" JPG_LIB="${JPG_LIB}" TAG="${TAG}-$CC" LMPFLAGS="${LMPFLAGS}"'

                sh 'ccache -s'
            }
        }
    } catch (err) {
        echo "Caught: ${err}"
        currentBuild.result = 'FAILURE'
    }
    step([$class: 'GitHubPRBuildStatusPublisher', buildMessage: [failureMsg: [content: 'Can\'t set status; build failed.'], successMsg: [content: 'Can\'t set status; build succeeded.']], statusMsg: [content: env.GITHUB_PR_COND_REF + ' run ended'], unstableAs: 'FAILURE'])

    step([$class: 'WarningsPublisher', canComputeNew: false, consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']], defaultEncoding: '', excludePattern: '', healthy: '', includePattern: '', messagesPattern: '', unHealthy: ''])
    step([$class: 'AnalysisPublisher', canComputeNew: false, defaultEncoding: '', healthy: '', unHealthy: ''])

    if (currentBuild.result == 'FAILURE') {
        slackSend channel: '#lammps-workshop', color: 'bad', message: "(WORKSHOP) Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend channel: '#lammps-workshop', color: 'good', message: "(WORKSHOP) Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
