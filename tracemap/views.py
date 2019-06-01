import re
import xmltodict
from batbox import settings
from datetime import datetime
from django.http import HttpResponse, Http404
from django.template import loader
from os import listdir, path


class TraceIdentifier:

    # eg PIPPIP_20190430_210112
    #   20150610_215446
    # String should exclude filetype

    def __init__(self, identifier_string):
        self.matched = False
        self.identified = False
        self.species = None
        self.genus = None
        self.datetime = None
        self.identifier_string = identifier_string
        match = re.match(
            r'^(?P<ident>(((?P<genus>\w{3})(?P<species>\w{3}))|(No_ID)|(NOISE))_)?(?P<date>\d{8})_(?P<time>\d{6})$',
            identifier_string
        )
        if match:
            self.matched = True
            fields = match.groupdict()
            date = fields['date']
            time = fields['time']
            self.datetime = datetime(
                int(date[0:4]),
                int(date[4:6]),
                int(date[6:8]),
                int(time[0:2]),
                int(time[2:4]),
                int(time[4:6])
            )
            if fields['ident'] and fields['genus']:
                self.identified = True
                self.genus = fields['genus']
                self.species = fields['species']

    def as_dict(self):
        return {
            'matched': self.matched,
            'identified': self.identified,
            'species': self.species,
            'genus': self.genus,
            'datetime': self.datetime,
        }

class Point:
    def __init__(self, id=None, lat=None, lon=None, description=None, style=None):
        self.id = id
        self.description = description
        self.style = style
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        return {
            'name': self.id,
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
            with open(map_file_path) as fd:
                kml = xmltodict.parse(fd.read())['kml']['Document']
                # map_data['styles'] = kml['Style']
                # Two types of placemark: containing Point or LineString
                points = [xml_dict_to_point(p) for p in kml['Placemark'] if 'Point' in p]

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


def xml_dict_to_point(data: dict) -> Point:
    point = Point()
    point.description = data['description']
    point.id = data['name']
    point.style = data['styleUrl']
    (point.lon, point.lat, _altitude) = data['Point']['coordinates'].split(',')
    return point


def bound_from_points(points: list):
    min_lat = min([p.lat for p in points])
    min_lon = min([p.lon for p in points])
    max_lat = max([p.lat for p in points])
    max_lon = max([p.lon for p in points])
    return (min_lat, min_lon), (max_lat, max_lon)
