node {
    def os = 'fedora'
    def version = 27

    stage('Checkout') {
        checkout([$class: 'GitSCM', branches: [[name: '*/master']], userRemoteConfigs: [[url: 'https://github.com/lammps/lammps-testing.git', credentialsId: 'lammps-jenkins']],
                  extensions: [[$class: 'PathRestriction', includedRegions: 'envs/'+os+'/'+version+'/.*']]
                 ])
    }


    docker.withRegistry('https://registry.hub.docker.com', 'docker-registry-login') {
        dir('envs/' + os + '/' + version + '/') {
            def image_name = 'rbberger/lammps-testing:' + os + '_' + version

            stage 'Build'
            docker.build(image_name)

            stage 'Publish'
            def image = docker.image(image_name)
            image.push()
        }
    }
}
