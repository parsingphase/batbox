Running the local server in development mode
============================================

To run with a server that responds instantly to changes in files, whether
backend, frontend or static, you'll need to use the Django development server.

To configure this, follow the steps in [RUNNING-LOCALLY.md](RUNNING-LOCALLY.md). 
Running the local server fully once is a good idea to make sure that everything's 
working before you start tweaking.

Once you've done that, stop the server with a few control-C's and continue below:

Firstly, run up the docker environment without starting the Apache server:

    host$ ./run-docker.sh bash
    ### Checking for rebuild...
    batbox
    Sending build context to Docker daemon  4.655kB
    Step 1/19 : FROM ubuntu:18.04
     ---> 7698f282e524
    ...
    Step 19/19 : CMD /root/buildAndRun.sh
     ---> Using cache
     ---> 71b5da5d7b46
    Successfully built 71b5da5d7b46
    Successfully tagged pyserver:latest
    
    ### Running container, mounting current directory at /var/www
    (venv) root@3b654280392e:/var/www# 

This won't fetch any libraries, import any audio files or start a web server; 
it'll just open the container with a bash shell, with the virtualenv activated.

**IMPORTANT** The virtualenv inside the container is transient; it'll need rebuilding 
when you start the container. It's found in `/var/venv` on the container. 

While developing, you'll probably want to create a different virtualenv native to your
host, to hold libraries for code completion. Mixing up the two is a great way of getting 
confused.

To build the project or import files, consult the command-line setup section of
 [RUNNING-SERVER.md](RUNNING-SERVER.md#command-line-setup).
 
The command you'll need to get the dependencies and set up files for the development 
environment is `make rebuild`.
  
### Run a web server in the container 
 
To run a server, you have two choices:

Run the django development server, which will respond instantly to *most* file
changes, but fails to play the audio in some browsers (it doesn't supply the Range
headers that Safari insists on for WAVs) 
 
    DJANGO_DEBUG=1 make runserver
 
To run apache, which won't respond to file changes but better simulates the production 
environment:

    DJANGO_DEBUG=1 /usr/sbin/apache2ctl -D FOREGROUND
    
Both of these should make the site available on your host at http://127.0.0.1:8088

### Manually built files

There are a few files that aren't managed directly by the development server:

- The LESS file at `tracemap/static/tracemap/css/recordings.less` needs to be recompiled
after editing. `make site_css` can do that.

- The URL router used by the javascript frontend also has to be manually rebuilt if 
`tracemap/urls.py`.  Use `make collect_static` for that.

If you've run the `make install` phase on your host as well as in the container,
these can be run in either location. 

To get a second shell in the container without stopping the webserver 
(to run any `make` or `manage.py` tasks), run `docker exec -it batbox bash`
