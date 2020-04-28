def project_url = 'https://github.com/lammps/lammps.git'

def lammps_branch = "master"

def container_definition = "tools/singularity/${params.CONTAINER_NAME}.def"
def container_file = "${params.CONTAINER_NAME}.sif"


node('atlas2') {
    stage('Checkout') {
        dir('lammps') {
            commit = checkout([$class: 'GitSCM', branches: [[name: "*/${lammps_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true],[$class: 'PathRestriction', excludedRegions: '', includedRegions: container_definition]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: 'https://github.com/lammps/lammps']]])
        }
    }

    stage('Build') {
        sh "singularity build --fakeroot ${container_file} ${container_definition}"
    }

    stage('Publish') {
        sh "cp -f ${container_file} /home/jenkins/containers/"
    }
}
