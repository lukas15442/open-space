#!/bin/bash
set -e

if ! whoami &> /dev/null; then
  if [ -w /etc/passwd ]; then
    echo "${USER_NAME:-default}:x:$(id -u):0:${USER_NAME:-default} user:${HOME}:/sbin/nologin" >> /etc/passwd
  fi
fi

# Docker image startup script
#
# Expects the following environment variables:
#
# OPENSUBMIT_SERVER_HOST: URL of the server installation

# (Re-)create OpenSubmit configuration from env variables
opensubmit-exec configcreate $OPENSUBMIT_SERVER_HOST

echo "Waiting for web server to start ..."
# Wait for web server to come up
until $(curl --output /dev/null --silent --head --fail $OPENSUBMIT_SERVER_HOST); do
    echo '... still waiting ...'
    sleep 5
done
echo "Web server started."

# Perform config test, triggers also registration
/usr/local/bin/opensubmit-exec configtest

echo "starting exec"
while [ 1 ]
do
   opensubmit-exec run >> /var/log/opensubmit 2>&1
   sleep 10
done