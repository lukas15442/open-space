FROM openshift/jenkins-2-centos7

USER root

RUN yum install -y epel-release && \
    yum install -y gcc gcc-c++ kernel-devel make valgrind openssh-server passwd ed cppunit \
                   cppunit-devel cmake llvm-toolset-7-clang llvm-toolset-7-lldb && \
    ln -s /opt/rh/llvm-toolset-7/root/bin/clang++ /usr/bin/clang++ && \
    ln -s /opt/rh/llvm-toolset-7/root/usr/bin/lldb /usr/bin/lldb

ADD ./sshd_config /etc/ssh/sshd_config

RUN chmod 775 /var/run && \
    rm -f /var/run/nologin && \
    adduser --system -s /bin/bash -u 1234321 -g 0 jenkins-ssh && \
    chmod 775 /etc/ssh /home && \
    chmod 660 /etc/ssh/sshd_config && \
    chmod 664 /etc/passwd /etc/group && \
    ssh-keygen -A

ADD ./start.sh /start.sh

RUN mkdir /opensubmit && \
    chgrp 0 /opensubmit && \
    chmod g=u /opensubmit && \
    chgrp -R 0 /etc/ssh && \
    chmod -R g=u /etc/ssh && \
    chmod +x /start.sh

EXPOSE 2222

USER jenkins-ssh
CMD /start.sh