#!/usr/bin/env bash

## Entrypoint script for the docker development image

set -e

echo '### Setting up the project - this could take a while'
cd /var/www
echo
echo '## Fetching dependencies'
echo
source /var/venv/bin/activate
make install
echo
echo '## Installing frontend assets'
make collect_static
echo
# Load any files in webroot/media
echo
echo '## Refreshing the local database…'
echo
python manage.py migrate
echo
echo '## Creating a default admin user, if needed'
echo
python manage.py createdefaultadmin FIRSTPASS.txt

if [[ "$1" != "--buildonly" ]]; then
    echo
    echo '## Looking for new audio files to import…'
    echo
    python manage.py importaudiofile -r webroot/media
    python manage.py importkmlfile -r webroot/media

    echo
    echo "## Running the web server. Ignore any message about the server's domain name…"
    echo "## You should now be able to access the project at http://127.0.0.1:8088"
    echo "## To stop the server, hit Control-C at least once"
    /usr/sbin/apache2ctl -D FOREGROUND
fi