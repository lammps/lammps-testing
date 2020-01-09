import jenkins.model.JenkinsLocationConfiguration
import hudson.security.csrf.DefaultCrumbIssuer
import jenkins.security.s2m.AdminWhitelistRule
import jenkins.model.Jenkins

jlc = JenkinsLocationConfiguration.get()
jlc.setUrl("https://ci.lammps.org/")
jlc.setAdminAddress("richard.berger@temple.edu")
jlc.save()
 
def instance = Jenkins.instance
instance.setCrumbIssuer(new DefaultCrumbIssuer(true))
instance.getInjector().getInstance(AdminWhitelistRule.class).setMasterKillSwitch(false)
instance.setSlaveAgentPort(-1)
instance.save()
