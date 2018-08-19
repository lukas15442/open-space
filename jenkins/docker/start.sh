#!/bin/bash

echo -e ",s/1234321/`id -u`/g\\012 w" | ed -s /etc/passwd
mkdir -p /home/jenkins-ssh/.ssh
touch /home/jenkins-ssh/.ssh/authorized_keys
chmod 700 /home/jenkins-ssh/.ssh
chmod 600 /home/jenkins-ssh/.ssh/authorized_keys

exec /usr/sbin/sshd -D &

/usr/bin/dumb-init -- /usr/libexec/s2i/run