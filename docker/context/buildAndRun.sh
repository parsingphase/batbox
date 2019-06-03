#!/usr/bin/env bash

set -e

echo '### Setting up the project - this could take a while'
cd /var/www
echo
echo '## Fetching dependencies'
echo
source /var/venv/bin/activate
pipenv install
echo
echo '## Installing frontend assets'
echo
python manage.py collectstatic --noinput
# Load any files in webroot/media
echo
echo '## Refreshing the local database…'
echo
python manage.py migrate
echo
echo '## Creating a default admin user, if needed'
echo
python manage.py createdefaultadmin FIRSTPASS.txt
echo
echo '## Looking for new audio files to import…'
echo
find webroot/media -name *.wav | xargs -iz python manage.py importaudiofile 'z'
find webroot/media -name *.kml | xargs -iz python manage.py importkmlfile 'z'

echo
echo "## Running the web server. Ignore any message about the server's domain name…"
echo "## You should now be able to access the project at http://127.0.0.1:8088"
echo "## To stop the server, hit Control-C at least once"
/usr/sbin/apache2ctl -D FOREGROUND