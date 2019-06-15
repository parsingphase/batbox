# Build tools - venv must be initialised beforehand
# SEE: https://blog.horejsek.com/makefile-with-python/ , https://www.giacomodebidda.com/pipenv/

SHELL := /bin/bash
VIRTUALENV ?= ./venv

.PHONY: gather_js collect_static install

gather_npm_assets:
	cp ./node_modules/bootstrap-datepicker/dist/js/bootstrap-datepicker.js assets/js/
	cp ./node_modules/bootstrap-datepicker/dist/css/bootstrap-datepicker.css assets/css/
	cp ./node_modules/timepicker/jquery.timepicker.js assets/js/
	cp ./node_modules/timepicker/jquery.timepicker.css assets/css/
	cp ./node_modules/datepair.js/dist/datepair.js assets/js
	cp ./node_modules/heatmap.js/build/heatmap.min.js assets/js
	cp ./node_modules/leaflet-heatmap/leaflet-heatmap.js assets/js

collect_static: gather_npm_assets
	python manage.py collectstatic --noinput

install:
	npm install
	source ${VIRTUALENV}/bin/activate; \
	pipenv install