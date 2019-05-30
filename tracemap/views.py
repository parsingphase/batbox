from batbox import settings
# from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
from os import listdir, path
import xmltodict


class Point:
    name = None
    description = None
    style = None
    lat = None
    lon = None

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'style': self.description,
            'position': (self.lat, self.lon)
        }


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
    audio_files = []
    map_files = []
    for file in data_files:
        if file[-4:] == '.wav':
            audio_files.append({
                'id': file[:-4],
                'filename': file,
                'path': session_path + '/' + file
            })
        elif file[-4:] == '.kml':
            map_files.append(file)
    # return HttpResponse(repr(data_files))
    map_data = {'points': []}
    if map_files:
        map_file = session_dir + '/' + map_files[0]
        with open(map_file) as fd:
            kml = xmltodict.parse(fd.read())['kml']['Document']
            # map_data['styles'] = kml['Style']
            # Two types of placemark: containing Point or LineString
            points = [xml_dict_to_point(p) for p in kml['Placemark'] if 'Point' in p]
            map_data['points'] = [p.as_dict() for p in points]
            map_data['bounds'] = bound_from_points(points)
    context = {
        'session_path': session_path,
        'session_name': session_name,
        'audio': audio_files,
        'map_data': map_data,
        'mapbox_token': settings.MAPS['mapbox_token'],
    }
    template = loader.get_template('tracemap/session.html')
    return HttpResponse(template.render(context, request))


def list_sessions(sessions_dir):
    sessions = [d for d in listdir(sessions_dir) if path.isdir(sessions_dir + '/' + d)]
    return sessions


def xml_dict_to_point(data: dict) -> Point:
    point = Point()
    point.description = data['description']
    point.name = data['name']
    point.style = data['styleUrl']
    (point.lon, point.lat, _altitude) = data['Point']['coordinates'].split(',')
    return point


def bound_from_points(points: list):
    min_lat = min([p.lat for p in points])
    min_lon = min([p.lon for p in points])
    max_lat = max([p.lat for p in points])
    max_lon = max([p.lon for p in points])
    return (min_lat, min_lon), (max_lat, max_lon)
