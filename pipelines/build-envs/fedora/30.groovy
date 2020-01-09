node {
    def os = 'fedora'
    def version = 29

    stage('Checkout') {
        checkout([$class: 'GitSCM', branches: [[name: '*/master']], userRemoteConfigs: [[url: 'https://github.com/lammps/lammps-testing.git', credentialsId: 'lammps-jenkins']],
                  extensions: [[$class: 'PathRestriction', includedRegions: 'envs/'+os+'/'+version+'/.*']]
                 ])
    }


    docker.withRegistry('http://glados2.cst.temple.edu:5000') {
        dir('envs/' + os + '/' + version + '/') {
            def image_name = 'lammps_testing:' + os + '_' + version

            stage 'Build'
            docker.build(image_name)

            stage 'Publish'
            def image = docker.image(image_name)
            image.push()
        }
    }
}
