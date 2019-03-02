package org.lammps.ci.build

class Documentation implements Serializable {
    protected def name
    protected def steps
	def message = ''

    Documentation(steps) {
        this.name = 'jenkins/build-docs'
        this.steps = steps
    }

    def configure() {
    }

    def build() {
        steps.stage('Generate HTML') {
            steps.sh 'make -C lammps/doc -j 8 html'
            steps.sh 'cd lammps/doc/html; tar cvzf ../lammps-docs.tar.gz *'
            steps.archiveArtifacts 'lammps/doc/lammps-docs.tar.gz'
        }

        steps.stage('Generate PDF') {
            steps.sh 'make -C lammps/doc pdf'
            steps.archiveArtifacts 'lammps/doc/Manual.pdf'
        }

        steps.stage('Check Spelling') {
            steps.sh 'make -C lammps/doc -j 8 spelling'
        }
    }

    def post_actions() {
        steps.recordIssues(tools: [steps.groovyScript('sphinx'), steps.groovyScript('spelling')])
    }
}
