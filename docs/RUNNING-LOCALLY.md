Running locally for testing or development
==========================================

These instructions should work on a Mac or Linux box. 
I've added a few Mac shortcuts as that's the system I'm working on.

It should be technically possible to run this under Windows, but I don't have a machine to test that on.


### Prerequisites

Before you start, you'll need a copy of Docker running on your system:

Visit [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop), 
and download, install and run "Docker Desktop" for your system.
You may need to create an account to be able to download Docker.


### Installation

First, get a copy of the code - either:
 
 - download and unpack the latest zipfile from 
 [https://github.com/parsingphase/batbox/releases](https://github.com/parsingphase/batbox/releases)

 - or fetch it with git:
 

    git clone git@github.com:parsingphase/batbox.git
 
Then, change into that directory in the console 
 
    cd batbox
    
prepare your settings file,
    
    cp batbox/settings.sample.py batbox/settings.py
    
and open it in a text editor (Mac console shortcut: `open -e batbox/settings.py`)    
    
To enable the maps in the site, you'll need a token from Mapbox. These are free for personal use.

To get one, visit [https://account.mapbox.com/access-tokens/](https://account.mapbox.com/access-tokens/) 
in your browser and follow thw instructions - you may need to create an account first.

(Mac console shortcut: `open https://account.mapbox.com/access-tokens/`)

You'll also need a long, random string to set as the SECRET_KEY. The easiest way to generate this on Mac or
Linux is to type:

    openssl rand -hex 50
    
and copy the result into your editor. Once you've changed those two lines, save `settings.py` and close the 
editor.

### Adding your recordings

Copy your bat recording audio files into `webroot/media/sessions` inside the project directory.
The layout doesn't matter so long as all your WAVs are somewhere in the `sessions` folder.

### Adding species data

The software can use the species list from [https://mammaldiversity.org](https://mammaldiversity.org) to provide 
full latin and common names for  the species detected. Download a copy of the CSV file from that site (either all 
species, or just bats) and save it as `data/asm-species.csv` (you'll probably have to rename the file). It will be 
processed when the server starts.

### Run the code

Once you've done the above once, you can start here every time you want to run the code.
    
In the project folder, run:    
    
    ./run-docker.sh
    
And wait. The first time you run, a local server is built that runs the code; the build isn't needed on
subsequent runs.

Once the server is built, it'll analyse and load your audio files. Any time you add files, just stop the
server and run `./run-docker.sh` again and they'll be found.

Finally, it'll start the server. Once you see:
    
    ## You should now be able to access the project at http://127.0.0.1:8088

you can open your browser and visit that address.

To access the admin part of the site, you'll need an admin password. The setup process creates this 
automatically - look in `FIRSTPASS.txt` in the project directory once the project has built. The username
that goes with this is `admin`.

### If you have problems

First, check that you've not missed any steps out above. Then, feel free to open an issue in Github at
[https://github.com/parsingphase/batbox/issues](https://github.com/parsingphase/batbox/issues)

### Finally, a note for developers

What you've built above is exactly the environment that the code is developed in - with one exception. 
The default server for the above environment doesn't reload the code when you edit it, so you won't
see any changes as you edit files. Instructions on how to run the development server locally 
can be found in [RUNNING-DEVELOPMENT.md].