@Library('lammps_testing')
import org.lammps.ci.LAMMPSBuild

node('atlas2') {
    def build = new LAMMPSBuild()
    build.regular_build(env.JOB_BASE_NAME)
}
