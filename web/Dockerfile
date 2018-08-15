# Dockerfile for OpenSubmit web application
#
# Note 1: This only works with PostgreSQL
# Note 2: A number of env variables is needed to run
#         the application. Check docker-entry.sh.

FROM ubuntu

# Prepare Apache environment
RUN apt-get update \
    && apt-get install -y locales apache2 apache2-utils python3 python3-pip libapache2-mod-wsgi-py3 netcat \
    && rm -rf /var/lib/apt/lists/* \
    && rm /etc/apache2/sites-enabled/000-default.conf \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8
COPY ./docker/httpd.conf /etc/apache2/sites-enabled/httpd.conf
COPY ./docker/docker-entry.sh /docker-entry.sh
COPY ./docker/ports.conf /etc/apache2

# Install dependencies explicitely for Docker caching
RUN mkdir /install
COPY requirements.txt /install
RUN pip3 install -r /install/requirements.txt psycopg2-binary

# Install existing wheel of OpenSubmit
# Call "make" if this step fails due to missing .whl files
COPY dist/*.whl /install
RUN pip3 install /install/*.whl

RUN chgrp 0 /etc && \
    chmod g=u /etc && \
    chgrp 0 /usr/local/lib/python3.6/dist-packages/opensubmit && \
    chmod g=u /usr/local/lib/python3.6/dist-packages/opensubmit && \
    chgrp 0 /var && \
    chmod g=u /var && \
    chgrp -R 0 /var/run && \
    chmod -R g=u /var/run && \
    chgrp -R 0 /var/lock && \
    chmod -R g=u /var/lock && \
    chgrp -R 0 /var/log && \
    chmod -R g=u /var/log && \
    chgrp -R 0 /var/log/apache2 && \
    chmod -R g=u /var/log/apache2 && \
    chmod g=u /etc/passwd

# Enable django-admin in interactive mode when running
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=opensubmit.settings \
    APACHE_RUN_DIR=/var/run \
    APACHE_PID_FILE=/var/lock/apache2.pid \
    APACHE_RUN_USER=default \
    APACHE_RUN_GROUP=root \
    APACHE_LOG_DIR=/var/log/apache2

USER 1001

EXPOSE 8080
ENTRYPOINT ["/docker-entry.sh"]
