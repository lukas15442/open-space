FROM openshift/jenkins-2-centos7

USER root

RUN yum install -y epel-release
RUN yum install -y cppcheck gcc gcc-c++ kernel-devel make valgrind

USER 1001
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/usr/libexec/s2i/run"]