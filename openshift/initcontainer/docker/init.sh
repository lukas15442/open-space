#!/bin/bash

# import realm
wget $GIT_URL/sso/realm-export.json

export TKN=$(curl -k "$SSO_URL/auth/realms/master/protocol/openid-connect/token" \
  -d "username=$SSO_USERNAME" \
  -d "password=$SSO_PASSWORD" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r ".access_token")

curl -k -v -X POST "$SSO_URL/auth/admin/realms" \
  -H "Content-Type:application/json" \
  -H "Authorization: Bearer $TKN" \
  -d "@/realm-export.json"


# import client opensubmit
wget $GIT_URL/sso/opensubmit.json

sed -i "s/{DOMAIN}/$WEB_DOMAIN/g" /opensubmit.json

export TKN=$(curl -k "$SSO_URL/auth/realms/master/protocol/openid-connect/token" \
  -d "username=$SSO_USERNAME" \
  -d "password=$SSO_PASSWORD" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r ".access_token")

curl -k -v -X POST "$SSO_URL/auth/admin/realms/hda/clients" \
  -H "Content-Type:application/json" \
  -H "Authorization: Bearer $TKN" \
  -d "@/opensubmit.json"


# import client jenkins
wget $GIT_URL/sso/jenkins.json

sed -i "s/{DOMAIN}/$JENKINS_DOMAIN/g" /jenkins.json

export TKN=$(curl -k "$SSO_URL/auth/realms/master/protocol/openid-connect/token" \
  -d "username=$SSO_USERNAME" \
  -d "password=$SSO_PASSWORD" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r ".access_token")

curl -k -v -X POST "$SSO_URL/auth/admin/realms/hda/clients" \
  -H "Content-Type:application/json" \
  -H "Authorization: Bearer $TKN" \
  -d "@/jenkins.json"


# change client secret from opensubmit and add admin rights
export TKN=$(curl -k "$SSO_URL/auth/realms/master/protocol/openid-connect/token" \
  -d "username=$SSO_USERNAME" \
  -d "password=$SSO_PASSWORD" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r ".access_token")

export OPENSUBMIT_ID=$(curl -k "$SSO_URL/auth/admin/realms/hda/clients" \
  -H "Authorization: Bearer $TKN" | jq -r '.[] | select(.clientId == "opensubmit") | .id')

export OPENSUBMIT_SECRET=$(curl -k "$SSO_URL/auth/admin/realms/hda/clients/$OPENSUBMIT_ID/client-secret" \
  -H "Authorization: Bearer $TKN" | jq -r ".value")

oc login $OC_URL && \
oc project $MY_POD_NAMESPACE && \
oc set env deploymentconfig/web OPENSUBMIT_LOGIN_OPENSHIFT_SSO_OIDC_RP_CLIENT_SECRET=$OPENSUBMIT_SECRET

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


# jenkins openid config
export TKN=$(curl -k "$SSO_URL/auth/realms/master/protocol/openid-connect/token" \
  -d "username=$SSO_USERNAME" \
  -d "password=$SSO_PASSWORD" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | jq -r ".access_token")

export JENKINS_ID=$(curl -k "$SSO_URL/auth/admin/realms/hda/clients" \
  -H "Authorization: Bearer $TKN" | jq -r '.[] | select(.clientId == "jenkins") | .id')

export JENKINS_SECRET=$(curl -k "$SSO_URL/auth/admin/realms/hda/clients/$JENKINS_ID/client-secret" \
  -H "Authorization: Bearer $TKN" | jq -r ".value")

export JENKINS_CRYPT_SECRET=$(curl -k --user 'admin:admin' --data-urlencode \
  "script=pw='$JENKINS_SECRET'; passwd_enc=hudson.util.Secret.fromString(pw).getEncryptedValue(); println(passwd_enc)" \
   https://$JENKINS_DOMAIN/scriptText)

wget $GIT_URL/jenkins/config.xml

sed -i "s/{USERNAME}/$JENKINS_ADMIN/g" /config.xml
sed -i "s,{SECRET},$JENKINS_CRYPT_SECRET,g" /config.xml

sed -i "s,{TOKEN_URL},$SSO_URL/auth/realms/hda/protocol/openid-connect/token,g" /config.xml
sed -i "s,{AUTH_URL},$SSO_URL/auth/realms/hda/protocol/openid-connect/auth,g" /config.xml
sed -i "s,{USERINFO_URL},$SSO_URL/auth/realms/hda/protocol/openid-connect/userinfo,g" /config.xml
sed -i "s,{LOGOUT_URL},$SSO_URL/auth/realms/hda/protocol/openid-connect/logout,g" /config.xml
sed -i "s,{REDIRECT_URL},https://$JENKINS_DOMAIN,g" /config.xml

wget --no-check-certificate https://$JENKINS_DOMAIN/jnlpJars/jenkins-cli.jar

export UPDATE_LIST=$( java -jar jenkins-cli.jar -auth admin:admin -noCertificateCheck \
  -s https://$JENKINS_DOMAIN list-plugins | grep -e ')$' | awk '{ print $1 }' );
if [ ! -z "${UPDATE_LIST}" ]; then
    echo Updating Jenkins Plugins: ${UPDATE_LIST};
    java -jar jenkins-cli.jar -auth admin:admin -noCertificateCheck \
      -s https://$JENKINS_DOMAIN install-plugin ${UPDATE_LIST};
fi

java -jar jenkins-cli.jar -auth admin:admin -noCertificateCheck \
      -s https://$JENKINS_DOMAIN install-plugin oic-auth valgrind warnings clang-scanbuild cppcheck;

\cp config.xml /jenkins/
rm -rf /jenkins/jobs/OpenShift\ Sample/

java -jar jenkins-cli.jar -auth admin:admin -noCertificateCheck \
  -s https://$JENKINS_DOMAIN safe-restart;

