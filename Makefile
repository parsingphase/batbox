# Build tools - venv must be initialised beforehand

SHELL := /bin/bash

.PHONY: gather_js collect_static install check_virtualenv migrate update remind_restart rebuild help test

help:
	#
	# BUILD TARGETS:
	#
	# NOTE: most targets require a virtual env to be activated and will fail if not
	#
	# install: Fetch JS and Python dependencies
	# rebuild: Rebuild project after a code update or git pull
	# migrate: Run any outstanding DB migrations
	# test: Run static code tests
	# collect_static: Rebuild and gather frontend assets
	# venv: Create a virtual env in ./venv if it's missing.
	#       This does not activate the environment; use source venv/bin/activate for that
	#
	echo "# Help will not be displayed if you use make -s, --silent or --quiet"

test:
	python -m flake8 -v --exclude=.idea,.git,venv

check_virtualenv:
	test -n "$(VIRTUAL_ENV)"  # Will fail if we're not in a VIRTUAL_ENV

check_settings: batbox/settings.py
	test -f batbox/settings.py || echo 'Please create the settings file at batbox/settings.py'  # Warn
	test -f batbox/settings.py  # Then fail if it's not there
	touch batbox/settings.py

site_css: tracemap/static/tracemap/css/recordings.less
	./node_modules/.bin/lessc tracemap/static/tracemap/css/recordings.less tracemap/static/tracemap/css/recordings.css

gather_npm_assets:
	rm -rf assets/vendor/js/* assets/vendor/css/* webroot/static/*
	cp ./node_modules/bootstrap/dist/css/bootstrap.min.css assets/vendor/css/
	cp ./node_modules/bootstrap/dist/js/bootstrap.min.js assets/vendor/js/
	cp ./node_modules/@fortawesome/fontawesome-free/css/all.min.css assets/vendor/css/fontawesome-all.min.css
	cp -r ./node_modules/@fortawesome/fontawesome-free/webfonts assets/vendor/
	cp ./node_modules/bootstrap-datepicker/dist/js/bootstrap-datepicker.min.js assets/vendor/js/
	cp ./node_modules/bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css assets/vendor/css/
	cp ./node_modules/jquery/dist/jquery.min.js assets/vendor/js/
	cp ./node_modules/timepicker/jquery.timepicker.min.js assets/vendor/js/
	cp ./node_modules/timepicker/jquery.timepicker.min.css assets/vendor/css/
	cp ./node_modules/datepair.js/dist/datepair.min.js assets/vendor/js/
	cp ./node_modules/leaflet/dist/leaflet.js assets/vendor/js/
	cp ./node_modules/leaflet/dist/leaflet.css assets/vendor/css/
	cp -r ./node_modules/leaflet/dist/images assets/vendor/css/
	cp ./node_modules/heatmap.js/build/heatmap.min.js assets/vendor/js/
	cp ./node_modules/leaflet-heatmap/leaflet-heatmap.js assets/vendor/js/
	cp ./node_modules/moment/min/moment.min.js assets/vendor/js/
	cp ./node_modules/datatables.net/js/jquery.dataTables.min.js assets/vendor/js/
	cp ./node_modules/datatables.net-dt/css/jquery.dataTables.min.css assets/vendor/css/
	cp -r ./node_modules/datatables.net-dt/images assets/vendor/images

collect_static: check_virtualenv site_css gather_npm_assets
	python manage.py collectstatic_js_reverse
	python manage.py collectstatic --noinput

install: check_virtualenv
	npm install
	pipenv install

migrate: check_virtualenv
	python manage.py migrate

venv: venv/bin/activate
	test -d venv || python3 -m venv venv
	touch venv/bin/activate   # update it in case date was old

remind_restart:
	echo -n; echo "** Remember to restart the webserver or WSGI server **"; echo -n

rebuild: check_virtualenv install collect_static migrate remind_restart
