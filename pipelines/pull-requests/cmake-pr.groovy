node('atlas2') {
    def build_name = 'jenkins/cmake-pr'
    def project_url = 'https://github.com/lammps/lammps.git'
    def testing_project_url = 'https://github.com/lammps/lammps-testing.git'
    def docker_image_name = 'rbberger/lammps-testing:ubuntu_latest'
    def cmake_options = ['-C ../lammps/cmake/presets/all_on.cmake',
                         '-D CMAKE_CXX_FLAGS="-Wall -Wextra -Wno-unused-result"',
                         '-D DOWNLOAD_VORO=on',
                         '-D PKG_MSCG=off',
                         '-D PKG_USER-LB=off',
                         '-D PKG_LATTE=off',
                         '-D PKG_KIM=off',
                         '-D PKG_USER-QUIP=off',
                         '-D PKG_USER-QMMM=off',
                         '-D PKG_USER-H5MD=off',
                         '-D PKG_USER-VTK=off',
                         '-D PKG_GPU=off',
                         '-D PKG_KOKKOS=off',
                         '-D PKG_USER-INTEL=off',
                         '-D PKG_USER-OMP=off',
                         '-D PKG_MPIIO=off',
                         '-D BUILD_MPI=off',
                         '-D BUILD_OMP=off']

    stage('Checkout') {
        dir('lammps') {
            branch_name = sprintf('origin-pull/pull/%s/merge', env.GITHUB_PR_NUMBER)
            refspec = sprintf('+refs/pull/%s/merge:refs/remotes/origin-pull/pull/%s/merge', env.GITHUB_PR_NUMBER, env.GITHUB_PR_NUMBER)
            checkout([$class: 'GitSCM', branches: [[name: branch_name]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CleanCheckout']], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', name: 'origin-pull', refspec: refspec, url: project_url]]])
        }

        dir('lammps-testing') {
            git branch: 'master', credentialsId: 'lammps-jenkins', url: testing_project_url
        }
    }

    gitHubPRStatus githubPRMessage('${GITHUB_PR_COND_REF} run started')

    stage('Setup') {
        def envImage = docker.image(docker_image_name)

        try {
            docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
                // ensure image is current
                envImage.pull()

                // use workaround (see https://issues.jenkins-ci.org/browse/JENKINS-34276)
                docker.image(envImage.imageName()).inside {
                    stage('Configure') {
                        sh 'rm -rf build'
                        sh 'mkdir build'
                        sh 'cd build && cmake ' + cmake_options.join(' ') + " ../lammps/cmake"
                    }

                    stage('Compile') {
                        sh 'make -C build -j 8'
                    }
                }
            }
            currentBuild.result = 'SUCCESS'
        } catch (err) {
            echo "Caught: ${err}"
            currentBuild.result = 'FAILURE'
        }
    }

    githubPRStatusPublisher statusMsg: githubPRMessage('${GITHUB_PR_COND_REF} run ended'), unstableAs: 'SUCCESS'

    warnings consoleParsers: [[parserName: 'GNU Make + GNU C Compiler (gcc)']]

    if (currentBuild.result == 'FAILURE') {
        slackSend color: 'bad', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} failed!"
    } else {
        slackSend color: 'good', message: "Build <${env.BUILD_URL}|#${env.BUILD_NUMBER}> of ${env.JOB_NAME} succeeded!"
    }
}
