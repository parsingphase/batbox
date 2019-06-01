from batbox import settings
from django.http import HttpResponse, Http404
from django.template import loader
from os import listdir, path
from tracemap.filetools import TraceIdentifier
from tracemap.datatypes import bound_from_points


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
    session_dir = sessions_dir + '/' + session_name
    session_path = settings.MEDIA_URL + 'sessions/' + session_name

    data_files = listdir(session_dir)
    traces = {}
    map_files = []

    for file in data_files:
        if file[-4:] == '.wav':
            id = file[:-4]
            traces[id] = {
                'id': id,
                'filename': file,
                'path': session_path + '/' + file,
                'id_data': TraceIdentifier(id).as_dict(),
                'location': None
            }
        elif file[-4:] == '.kml':
            map_files.append(file)

    bounds = None
    points = []
    if map_files:
        for map_file in map_files:
            map_file_path = session_dir + '/' + map_file

        bounds = bound_from_points(points)

    for point in points:
        if point.id in traces:
            traces[point.id]['location'] = point.as_dict()

    context = {
        'session_path': session_path,
        'session_name': session_name,
        'map_data': {'traces': traces, 'bounds': bounds},
        'mapbox_token': settings.MAPS['mapbox_token'],
    }
    template = loader.get_template('tracemap/session.html')
    return HttpResponse(template.render(context, request))


def list_sessions(sessions_dir):
    sessions = [d for d in listdir(sessions_dir) if path.isdir(sessions_dir + '/' + d)]
    sessions.sort()
    return sessions
