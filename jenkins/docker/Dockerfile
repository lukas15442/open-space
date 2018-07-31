FROM openshift/jenkins-2-centos7

USER root

RUN yum install -y epel-release
RUN yum install -y gcc gcc-c++ kernel-devel make valgrind clang clang-analyzer

USER 1001
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/usr/libexec/s2i/run"]