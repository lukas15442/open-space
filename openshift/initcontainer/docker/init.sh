#!/bin/bash

oc login $OC_URL

# make admin in opensubmit
psql postgresql://opensubmit:opensubmit@db/opensubmit << EOF
     \set jenkinsAdmin `echo "$JENKINS_ADMIN"`
     \set adminFirstName `echo "$ADMIN_FIRST_NAME"`
     \set adminLastName `echo "$ADMIN_LAST_NAME"`
     \set opensubmitAdminMail `echo "$OPENSUBMIT_ADMIN_MAIL"`

     INSERT INTO auth_user
     (username, is_superuser, is_staff, password, first_name, last_name, email, is_active, date_joined)
     VALUES (:'jenkinsAdmin', true, true, 'None', :'adminFirstName', :'adminLastName', :'opensubmitAdminMail', true, now());

     INSERT INTO opensubmit_userprofile
     (user_id, student_id)
     VALUES ((SELECT id FROM auth_user WHERE username=:'jenkinsAdmin'), :'jenkinsAdmin')
EOF


# jenkins api and admin user
curl -k --user 'admin:admin' --data-urlencode \
  "script=import jenkins.model.*; import hudson.security.*; def instance = Jenkins.getInstance(); \
          def hudsonRealm = new HudsonPrivateSecurityRealm(false); hudsonRealm.createAccount('api', '$JENKINS_API_PASSWORD'); \
          instance.setSecurityRealm(hudsonRealm); instance.save()" \
   https://$JENKINS_DOMAIN/scriptText

curl -k --user 'admin:admin' --data-urlencode \
  "script=import jenkins.model.*; import hudson.security.*; def instance = Jenkins.getInstance(); \
          def strategy = new GlobalMatrixAuthorizationStrategy(); \
          strategy.add(Jenkins.ADMINISTER, 'api'); \
          strategy.add(Jenkins.ADMINISTER, 'admin'); \
          strategy.add(Jenkins.ADMINISTER, '$JENKINS_ADMIN'); \
          instance.setAuthorizationStrategy(strategy)" \
   https://$JENKINS_DOMAIN/scriptText


# read jenkins api token
# you have to generate manually the token in the jenkins gui, because reasons
export JENKINS_API_TOKEN=$(curl -k --user "api:$JENKINS_API_PASSWORD" --data-urlencode \
  "script=import jenkins.security.*; User u = User.get('api'); ApiTokenProperty t = u.getProperty(ApiTokenProperty.class); \
          def token = t.getApiToken(); println (token)" \
   https://$JENKINS_DOMAIN/scriptText)


# jenkins install and update plugins
wget --no-check-certificate https://$JENKINS_DOMAIN/jnlpJars/jenkins-cli.jar

export UPDATE_LIST=$( java -jar jenkins-cli.jar -auth admin:admin -noCertificateCheck \
  -s https://$JENKINS_DOMAIN list-plugins | grep -e ')$' | awk '{ print $1 }' );
if [ ! -z "${UPDATE_LIST}" ]; then
    echo Updating Jenkins Plugins: ${UPDATE_LIST};
    java -jar jenkins-cli.jar -auth admin:admin -noCertificateCheck \
      -s https://$JENKINS_DOMAIN install-plugin ${UPDATE_LIST};
fi

java -jar jenkins-cli.jar -auth admin:admin -noCertificateCheck \
      -s https://$JENKINS_DOMAIN install-plugin valgrind warnings clang-scanbuild cppcheck xunit git gitlab-oauth;


# jenkins delete openshift sample
echo " \
    rm -rf /var/lib/jenkins/jobs/OpenShift\ Sample/ \
" > jenkinsScript

export JENKINS_POD_NAME=$(oc get pods | grep -o "jenkins\S*")
export EXEC_POD_NAME=$(oc get pods | grep -o "exec\S*")

oc cp jenkinsScript $JENKINS_POD_NAME:./
oc exec $JENKINS_POD_NAME -- chmod +x jenkinsScript
oc exec $JENKINS_POD_NAME -- bash -c ./jenkinsScript


# jenkins gitlab auth
oc cp $JENKINS_POD_NAME:var/lib/jenkins/config.xml jenkinsConfig

sed -i ':a;N;$!ba;s|<securityRealm.*\n.*\n.*\n.*securityRealm>|<securityRealm class="org.jenkinsci.plugins.GitLabSecurityRealm"> \
    <gitlabWebUri>https://code.fbi.h-da.de</gitlabWebUri> \
    <gitlabApiUri>https://code.fbi.h-da.de</gitlabApiUri> \
    <clientID>'"$OPENSUBMIT_LOGIN_GITLAB_JENKINS_OAUTH_KEY"'</clientID> \
    <clientSecret>'"$OPENSUBMIT_LOGIN_GITLAB_JENKINS_OAUTH_SECRET"'</clientSecret> \
  </securityRealm>|g' \
jenkinsConfig

sed -i 's#<permission>hudson.model.Hudson.Administer:admin</permission>##g' jenkinsConfig

oc cp jenkinsConfig $JENKINS_POD_NAME:/var/lib/jenkins/config.xml


# executor ssh config for jenkins
oc exec $EXEC_POD_NAME -- ssh-keygen -t rsa -f /ssh/key -N ''
oc cp $EXEC_POD_NAME:ssh/key.pub ./
oc exec $JENKINS_POD_NAME -- mkdir /var/lib/jenkins/ssh
oc cp key.pub $JENKINS_POD_NAME:/var/lib/jenkins/ssh/authorized_keys


# restart jenkins
java -jar jenkins-cli.jar -auth admin:admin -noCertificateCheck \
  -s https://$JENKINS_DOMAIN safe-restart;


# set jenkins api token to exec
oc project $MY_POD_NAMESPACE && \
oc set env deploymentconfig/exec JENKINS_API_TOKEN=$JENKINS_API_TOKEN