from batbox import settings
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import HttpResponse, Http404
from django.template import loader
from os import listdir, path
from tracemap.models import AudioRecording
from typing import List


# Create your views here.
def index(request):
    template = loader.get_template('tracemap/days_index.html')
    context = {
        'days': list_counts_by_day(),
    }
    return HttpResponse(template.render(context, request))


def day_view(request, date):
    if date == 'undated':
        files = AudioRecording.objects.filter(recorded_at__isnull=True)
    else:
        (year, month, day) = date.split('-')
        date_start = datetime(int(year), int(month), int(day))
        date_end = date_start + timedelta(days=1)
        files = AudioRecording.objects.filter(
            recorded_at__range=(date_start, date_end)
        )

    if not len(files):
        raise Http404("No records")

    bounds = bounds_from_recordings(files)

    traces = [f.as_serializable() for f in files]

    context = {
        'title': date,
        'files': files,  # Non-flattened
        'map_data': {'traces': traces, 'bounds': bounds},  # for JSON
        'mapbox_token': settings.MAPS['mapbox_token'],
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
    template = loader.get_template('tracemap/session.html')
    return HttpResponse(template.render(context, request))


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

    files = AudioRecording.objects.filter(  # type: List[AudioRecording]
        file__contains=session_name
    )

    bounds = bounds_from_recordings(files)

    traces = [f.as_serializable() for f in files]

    context = {
        'title': session_name,
        'files': files,  # Non-flattened
        'map_data': {'traces': traces, 'bounds': bounds},
        'mapbox_token': settings.MAPS['mapbox_token'],
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
    }
    template = loader.get_template('tracemap/session.html')
    return HttpResponse(template.render(context, request))


def bounds_from_recordings(files):
    positioned_files = [f for f in files if f.latitude is not None]
    if len(positioned_files):
        bounds = (
            (
                min([t.latitude for t in positioned_files]),
                min([t.longitude for t in positioned_files])
            ),
            (
                max([t.latitude for t in positioned_files]),
                max([t.longitude for t in positioned_files])
            )
        )

        # Possibly not needed, leaflet.js may handle this
        if bounds[0] == bounds[1]:
            bounds = (
                (bounds[0][0] - 0.01, bounds[0][1] - 0.01),
                (bounds[0][0] + 0.01, bounds[0][1] + 0.01)
            )
    else:
        bounds = None
    return bounds


def list_sessions(sessions_dir):
    sessions = [
        d for d in listdir(sessions_dir) if path.isdir(sessions_dir + '/' + d)
    ]
    sessions.sort()
    return sessions


def list_counts_by_day():
    days = AudioRecording.objects.annotate(day=TruncDay('recorded_at')) \
        .values('day').annotate(c=Count('id')) \
        .values('day', 'c').order_by('day')

    return days


def list_view(request):
    files = AudioRecording.objects.all()

    traces = [audio_for_json(f) for f in files]
    bounds = bounds_from_recordings(files)

    template = loader.get_template('tracemap/list.html')
    context = {
        'map_data': {'traces': traces, 'bounds': bounds},
        'mapbox_token': settings.MAPS['mapbox_token'],
    }
    return HttpResponse(template.render(context, request))


def audio_for_json(audio: AudioRecording) -> dict:
    if audio is not None:
        j = audio.as_serializable()
        j['url'] = settings.MEDIA_URL + path.relpath(
            j['file'], settings.MEDIA_ROOT
        )
        j['file'] = None
    else:
        j = None

    return j
