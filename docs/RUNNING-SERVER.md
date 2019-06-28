Running on a server for public view
===================================

### Prerequisites

Installation has only been tested on Linux servers. If you want to run this under IIS, you're on your own.

- Firstly, you'll need Python 3.6+, plus pipenv. You'll also need npm to build the frontend code

- All the clever subsampling and spectrogram generation is done by [SoX](http://sox.sourceforge.net), which will need 
to be installed on your server

- Make sure you've got a mapbox token from https://account.mapbox.com/access-tokens/

- Download the ASM database (either the whole thing, or just the bats) in CSV format from https://mammaldiversity.org

- You won't need Docker for a production deploy; it can run under most webservers

- Sqlite can be used for a small install, but if you want to use MySQL, create the database as UTF8

### First installation

Clone the code

    git clone git@github.com:parsingphase/batbox.git
    
(or download a release build)

Configure the settings

    cp batbox/settings.sample.py batbox/settings.py
    vim settings.py
    
Make sure you set the mapbox token, update the secret, and add your production web hostname to `ALLOWED_HOSTS`

Create a python environment

    make pipenv
    
Configure the webserver

This bit's not simple. Python WSGI apps can run under various servers - consult the documentation for your own server.
This is a Django 2.2 site, so you can also check their [deployment guide](https://docs.djangoproject.com/en/2.2/howto/deployment/) 
 
If you just want a working Apache2 config file, take a look at [batbox.conf](prod-config/batbox.conf) and adapt to your needs.


### Build the code

(for subsequent code updates, after you're updated the source, restart from here)

Activate the virtualenv

    source venv/bin/activate
    
~~Draw the rest of the owl~~ Run the provided setup script

    make rebuild
    
This performs npm and python dependency installs, migrates the database, and moves various files to where they're needed    

### Command-line setup

If you're using a sqlite database, it will be in the `data` directory by default. You'll need to ensure that both the 
directory and database files (once created) are writable by both the web user and command-line user.

Before making the site public, you'll want to import some data.

Your audio files will need to live inside the project in `webroot/media/sessions`, so that they can be served alongside the site

Once these are in place, import them (make sure the virtualenv is activated) with `./manage.py importaudiofile -r webroot/media/sessions`

If you've got any KML auxiliary files (Wildlife Acoustics recorders produce these, but they're not usually essential), you
can store them alongside the audio and import them with
`./manage.py importkmlfile -r webroot/media/sessions` *after* the audio files

You can also import species names from the ASM database with `./manage.py importspecieslist PATH/TO/asm-species.csv`. It
doesn't matter when you do this.

Finally, you'll probably want to create an admin user with `./manage.py createsuperuser`

### Restart the web server

This depends on your system; it's necessary because the WSGI app won't usually re-read changed files between restarts,
unlike other interfaces such as FCGI.


## Problems?

Open an issue in Github at https://github.com/parsingphase/batbox/issues
