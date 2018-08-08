FROM centos:latest

ADD ./origin.repo /etc/yum.repos.d/origin.repo

RUN \
  yum install -y epel-release && \
  yum update && \
  yum install -y wget curl jq origin-clients unzip zip

ADD ./init.sh /init.sh
RUN chmod +x /init.sh

ADD ./sleep.sh /sleep.sh
RUN chmod +x /sleep.sh

ENTRYPOINT /sleep.sh