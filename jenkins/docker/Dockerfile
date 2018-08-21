FROM openshift/jenkins-2-centos7

USER root

RUN yum install -y epel-release
RUN yum install -y gcc gcc-c++ kernel-devel make valgrind clang clang-analyzer openssh-server passwd ed cppunit \
                    cppunit-devel cmake

ADD ./sshd_config /etc/ssh/sshd_config
RUN chmod 775 /var/run
RUN rm -f /var/run/nologin

RUN adduser --system -s /bin/bash -u 1234321 -g 0 jenkins-ssh
RUN chmod 775 /etc/ssh /home
RUN chmod 660 /etc/ssh/sshd_config
RUN chmod 664 /etc/passwd /etc/group

RUN ssh-keygen -A

ADD ./start.sh /start.sh

RUN mkdir /opensubmit
RUN chgrp 0 /opensubmit && \
    chmod g=u /opensubmit && \
    chgrp -R 0 /etc/ssh && \
    chmod -R g=u /etc/ssh && \
    chmod +x /start.sh

EXPOSE 2222

USER jenkins-ssh
CMD /start.sh