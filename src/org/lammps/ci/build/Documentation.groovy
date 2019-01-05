package org.lammps.ci.build

class Documentation implements Serializable {
    protected def name
    protected def steps

    Documentation(steps) {
        this.name = 'jenkins/build-docs'
        this.steps = steps
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
        steps.warnings canComputeNew: false, canResolveRelativePaths: false, canRunOnFailed: true, categoriesPattern: 'RemovedInSphinx20Warning', consoleParsers: [[parserName: 'Sphinx Spelling Check'],[parserName: 'Sphinx Documentation Build']], defaultEncoding: '', excludePattern: '', failedTotalAll: '1', healthy: '0', includePattern: '', messagesPattern: '', unHealthy: '1', unstableTotalAll: '1'
    }
}
