def project_url = 'https://github.com/lammps/lammps-testing.git'

def lammps_branch = "master"

def container_definition = "containers/singularity/${currentBuild.projectName}.def"
def container_file = "${currentBuild.projectName}.sif"


node('atlas2') {
    cleanWs()

    stage('Checkout') {
        checkout([$class: 'GitSCM', branches: [[name: "*/${lammps_branch}"]], doGenerateSubmoduleConfigurations: false, extensions: [[$class: 'PathRestriction', includedRegions: "${container_definition}"], [$class: 'CloneOption', depth: 1, noTags: false, reference: '', shallow: true]], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'lammps-jenkins', url: project_url]]])
    }

    stage('Build') {
        sh "singularity build --force --fakeroot ${container_file} ${container_definition}"
    }

    stage('Publish') {
        sh "cp -f ${container_file} /mnt/lammps/containers/"
    }
}
