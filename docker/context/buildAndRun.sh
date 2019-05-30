#!/usr/bin/env bash

set -e

echo Running buildAndRun.sh
cd /var/www
source /var/venv/bin/activate
pipenv install
/usr/sbin/apache2ctl -D FOREGROUND