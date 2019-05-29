#!/usr/bin/env bash

set -e

get_script_dir () {
    SOURCE="${BASH_SOURCE[0]}"
    SOURCE_DIR=$( dirname "$SOURCE" )
    SOURCE_DIR=$(cd -P ${SOURCE_DIR} && pwd)
    echo ${SOURCE_DIR}
}

SCRIPT_DIR="$( get_script_dir )"
PARENT_DIR=$( dirname "$SCRIPT_DIR" )

cd ${SCRIPT_DIR}

echo Checking for rebuild...
docker rm batbox
docker build -t pyserver -f docker/Dockerfile docker/context

echo Running container, mounting current directory at /var/www
docker run -it -d -p 8088:80 \
    -v ${PARENT_DIR}:/var/www \
    -v ${SCRIPT_DIR}/docker/sites-enabled:/etc/apache2/sites-enabled \
    -v ${SCRIPT_DIR}/docker/logs:/var/log \
    --name batbox pyserver \
    "$@"
# -p, -v are host:container

# To get inside:
#  docker exec -it batbox bash

