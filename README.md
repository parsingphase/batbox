# batbox

### Dev notes

Lazy file serving: 
 - https://docs.djangoproject.com/en/1.11/howto/static-files/#serving-files-uploaded-by-a-user-during-development

Proper file serving: 
 - https://zacharyvoase.com/2009/09/08/sendfile/
 - https://www.nginx.com/resources/wiki/start/topics/examples/xsendfile/
 
Might need to be swicthable between Apache and Nginx depending on where it's to be served & what webserver I'm running there.