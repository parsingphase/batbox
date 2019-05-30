from batbox import settings
# from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from os import listdir, path


# Create your views here.
def index(request):
    session_name = request.GET.get('session', '')

    template = loader.get_template('tracemap/index.html')
    sessions_dir = settings.MEDIA_ROOT + 'sessions'
    sessions = [d for d in listdir(sessions_dir) if path.isdir(sessions_dir + '/' + d)]

    if session_name not in sessions:
        session_name = sessions[0]  # FIXME do something better here

    session_dir = sessions_dir + '/' + session_name
    session_path = settings.MEDIA_URL + 'sessions/' + session_name

    data_files = listdir(session_dir)

    audio_files = []
    map_files = []

    for file in data_files:
        if file[-4:] == '.wav':
            audio_files.append(file)
        elif file[-4:] == '.kml':
            map_files.append(file)

    # return HttpResponse(repr(data_files))

    context = {
        'session_path': session_path,
        'session_name': session_name,
        'audio': audio_files
    }
    return HttpResponse(template.render(context, request))
