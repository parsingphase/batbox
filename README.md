# batbox

### Visualisation utility for Wildlife Acoustics and GUANO-tagged data exports

![Map view](docs/images/mapview.png)         

[Wildlife Acoustics](https://www.wildlifeacoustics.com) are a manufacturer of 
wildlife audio tracking tools, from hobbyist to professional.
 
[GUANO](https://guano-md.org) is a standardised tag format for recordings of 
bat echolocation calls.
 
This utility is designed to help sort and visualise data exported from these tools 
by providing a map and time-based interface to audio recordings. 
It works best with GUANO-tagged files, but can also WAV files from Wildlife Acoustics 
exports with or without these tags, so long as the related KML files are also present.

So far it's been tested with the output of an 
[Echo Meter Touch 2 Bat Detector](https://www.wildlifeacoustics.com/products/echo-meter-touch-2).

Your recording files should be stored under the `webroot/media/sessions` folder.

    webroot/
        media/
            sessions/
                Session 20130401_053030/
                   MYOBRA_20180626_215501.wav
                   ...
                   Session 20180626_214348.kml
                   
### Configuration

The only configuration required is in [`settings_local.sample.py`](settings_local.sample.py), which is documented internally.
Copy this to `settings_local.py` and edit as required.                   
                   
### Running the code

The code is not yet built for production deployment. You can test it on a local computer using
[Docker](https://docker.com). Once that's installed you can run

    ./run-docker.sh
    
then (if all works) view the site in a browser at http://127.0.0.1:8088

Note that the first build will take a significant time and download a large amount of data.

Each time the server is restarted it will index any new files in the media folder.

### Code status

The code is in a very early form (3 days old!) and frankly isn't ready for anything.
           
                   