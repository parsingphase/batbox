# batbox
### Dev notes

Lazy file serving: 
 - https://docs.djangoproject.com/en/1.11/howto/static-files/#serving-files-uploaded-by-a-user-during-development

Proper file serving: 
 - https://zacharyvoase.com/2009/09/08/sendfile/
 - https://www.nginx.com/resources/wiki/start/topics/examples/xsendfile/
 
Might need to be switchable between Apache and Nginx depending on where it's to be served & what webserver I'm running there.

Nginx: 
 - https://medium.com/@greut/minimal-python-deployment-on-docker-with-uwsgi-bc5aa89b3d35
 - https://github.com/dockerfiles/django-uwsgi-nginx
 
GUANO WAV metadata:
 - https://www.wildlifeacoustics.com/SCHEMA/GUANO.html 
 
Filenames:

From user guide: https://www.wildlifeacoustics.com/images/documentation/EMT-IOS-GUIDE.pdf
    
    3.1 Filenames for Recordings
    Recordings use the following naming convention:
      
    ID
    ID_YYYYMMDD_HHMMSSWAV
    The first three letters of the species and the first three letters of the genus for recordings that have been identified, NoID if Echo Meter Touch was unable to identify the recording or NOISE if the no bats are detected in the recording.
    YYYYMMDD_HHMMSS
    The full timestamp including the year, month, day, hour, minute, and second when the recording started.
     
     