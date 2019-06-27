Running on a server for public view
===================================

Full documentation will follow shortly.

In the meantime, here are some hints:

- This is a Django site, designed for Python 3.7 and Django 2.2. Django's software is great, but their 
[deployment guide](https://docs.djangoproject.com/en/2.2/howto/deployment/) is a little lacking.

- You'll need to copy [batbox/settings.sample.py](../batbox/settings.sample.py) to `batbox/settings.py`
and edit the top section marked


    #########################################################
    # Change these for your own installation:
    #########################################################
        
- You can use the default sqlite database for small installs, but you'll need to make sure that both it
and the directory containing it (`./data` by default) are writable by the both the web server, and the user that 
you run any command-line operations as.

- Python WSGI apps can run under various servers - consult the documentation for your own server. But if you just want 
a working Apache2 config file, take a look at [batbox.conf](prod-config/batbox.conf) and adapt to your needs.

- All the clever subsampling and spectrogram generation is done by [SoX](http://sox.sourceforge.net), which will need 
to be installed on your server.

- Make sure you've activated the Python virtualenv before doing anything below.


    source venv/bin/activate

- There are a bunch of build tasks in the Makefile in the project directory. Running `make` in that folder will give
you some hints:


    $ make
    #
    # BUILD TARGETS:
    #
    # NOTE: most targets require a virtual env to be activated and will fail if not
    #
    # install:         Fetch JS and Python dependencies
    # rebuild:         Rebuild project after a code update or git pull
    # migrate:         Run any outstanding DB migrations
    # test:            Run static code tests
    # collect_static:  Rebuild and gather frontend assets
    # runserver:       Run development server on port 80
    # venv:            Create a virtual env in ./venv if it's missing.
    #                  This does not activate the environment; use source venv/bin/activate for that
    #
    echo "# Help will not be displayed if you use make -s, --silent or --quiet"
    # Help will not be displayed if you use make -s, --silent or --quiet
    
- The importer scripts are standard Django commands accessed via `manage.py`. Running this will give you various clues.


    $ python3 manage.py 
    Type 'manage.py help <subcommand>' for help on a specific subcommand.
    Available subcommands:
    ...
    
    [tracemap]
        createdefaultadmin
        importasmspecieslist
        importaudiofile
        importkmlfile
