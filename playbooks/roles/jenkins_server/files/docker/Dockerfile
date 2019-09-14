FROM jenkins/jenkins:lts
ENV JAVA_OPTS="-Djenkins.CLI.disabled=true -Djenkins.install.runSetupWizard=false -Dorg.jenkinsci.plugins.github_branch_source.GitHubSCMSource.cacheSize=0"
COPY base.groovy /usr/share/jenkins/ref/init.groovy.d/base.groovy
COPY executors.groovy /usr/share/jenkins/ref/init.groovy.d/executors.groovy
COPY security.groovy /usr/share/jenkins/ref/init.groovy.d/security.groovy
COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN /usr/local/bin/install-plugins.sh < /usr/share/jenkins/ref/plugins.txt
