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
    python manage.py importaudiofile --subsample --spectrogram -r webroot/media/sessions
    python manage.py importkmlfile -r webroot/media/sessions

    if [[ -f "data/asm-species.csv" ]]; then
        echo "## Loading asm-species.csv"
        python manage.py importasmspecieslist data/asm-species.csv
    else
        echo "## asm-species.csv not found, see docs for details"
    fi

    echo
    echo "## Running the web server. Ignore any message about the server's domain name…"
    echo "## You should now be able to access the project at http://127.0.0.1:8088"
    echo "## To stop the server, hit Control-C at least once"

    set +e # make sure we report if the server errors
    /usr/sbin/apache2ctl -D FOREGROUND

    echo "## Server stopped"
fi