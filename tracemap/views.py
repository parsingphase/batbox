from batbox import settings
from django.http import HttpResponse, Http404
from django.template import loader
from os import listdir, path
from tracemap.models import AudioRecording
from typing import List


# Create your views here.
def index(request):
    session_name = request.GET.get('session', None)
    if session_name:
        return display_session(request, session_name)
    else:
        return display_index(request)


def get_session_dir():
    return settings.MEDIA_ROOT + 'sessions'


def display_index(request):
    template = loader.get_template('tracemap/index.html')
    sessions_dir = get_session_dir()
    sessions = list_sessions(sessions_dir)
    context = {
        'sessions': sessions
    }
    return HttpResponse(template.render(context, request))


def display_session(request, session_name):
    sessions_dir = get_session_dir()
    sessions = list_sessions(sessions_dir)
    if session_name not in sessions:
        raise Http404("No such session")

    files = AudioRecording.objects.filter(file__contains=session_name)  # type: List[AudioRecording]

    if len(files):
        bounds = (
            (min([t.latitude for t in files]), min([t.longitude for t in files])),
            (max([t.latitude for t in files]), max([t.longitude for t in files]))
        )
    else:
        bounds = None

    traces = [f.as_serializable() for f in files]

    context = {
        'session_name': session_name,
        'map_data': {'traces': traces, 'bounds': bounds},
        'mapbox_token': settings.MAPS['mapbox_token'],
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
    template = loader.get_template('tracemap/session.html')
    return HttpResponse(template.render(context, request))


def list_sessions(sessions_dir):
    sessions = [d for d in listdir(sessions_dir) if path.isdir(sessions_dir + '/' + d)]
    sessions.sort()
    return sessions
