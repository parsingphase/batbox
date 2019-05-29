# Based on: https://github.com/Craicerjack/apache-flask
FROM ubuntu:18.04

MAINTAINER Richard George <richard@phase.org>

RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi-py3 \
    build-essential \
    python3 \
    python3-dev\
    python3-pip \
    python3-venv \
    vim \
    git \
 && apt-get clean

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8


RUN pip3 install pipenv
RUN a2enmod headers

VOLUME /var/log
VOLUME /var/www

RUN a2dissite 000-default.conf

EXPOSE 80

RUN python3 -m venv /var/venv
ENV PYTHONPATH=/var/venv

RUN echo source /var/venv/bin/activate >> /root/.bashrc

WORKDIR /var/www

# CMD ["/bin/bash"]
CMD  /usr/sbin/apache2ctl -D FOREGROUND