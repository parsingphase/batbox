# Build tools - venv must be initialised beforehand

SHELL := /bin/bash

.PHONY: gather_js collect_static install

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

collect_static: gather_npm_assets
	python manage.py collectstatic --noinput

install:
	npm install
	pipenv install