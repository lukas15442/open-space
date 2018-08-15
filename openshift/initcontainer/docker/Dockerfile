FROM centos:latest

ADD ./origin.repo /etc/yum.repos.d/origin.repo

RUN \
  yum install -y epel-release && \
  yum update && \
  yum install -y wget curl jq origin-clients unzip zip java-1.8.0-openjdk postgresql

RUN mkdir /working && mkdir /.kube

ADD ./init.sh /working/init.sh
RUN chmod +x /working/init.sh

ADD ./sleep.sh /working/sleep.sh
RUN chmod +x /working/sleep.sh

RUN chmod g=u /etc/passwd && \
    chgrp 0 /working && \
    chmod g=u /working && \
    chgrp 0 /.kube && \
    chmod g=u /.kube

USER 1001

ENTRYPOINT /working/sleep.sh