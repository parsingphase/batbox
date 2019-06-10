from batbox import settings
from datetime import datetime, timedelta, date
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import HttpResponse, Http404
from django.template import loader
from json import dumps
from os import listdir, path
from tracemap.models import AudioRecording
from svg_calendar import GridImage
from svgwrite.container import Hyperlink
from svgwrite import shapes


def decorate_rect_with_class(rect: shapes.Rect, day: date, _):
    day_string = day.strftime('%Y-%m-%d')
    outer = Hyperlink('/byday/' + day_string, '_self')
    rect.update({'class_': 'dateTrigger'})
    rect.update({'id': 'calday-' + day_string})
    outer.add(rect)
    return outer


# Create your views here.
def index(request):
    """
    Create a list of days with recordings

    Args:
        request:

    Returns:

    """
    template = loader.get_template('tracemap/days_index.html')
    summary, genuses = summarise_by_day()
    days = sorted(summary.values(), key=lambda d: d['day'] if d['day'] is not None else '')

    counts_by_day = {d: summary[d]['count'] for d in summary if d is not None}

    grid_image = GridImage().set_day_rect_decorator(decorate_rect_with_class)
    image = grid_image.draw_daily_count_image(counts_by_day, True).tostring()

    context = {
        'days': days,
        'genuses': genuses,
        'calendar_svg': image,
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

    return display_recordings_list(files, request, {'title': f'Date: {date}'})


def get_session_dir():
    return settings.MEDIA_ROOT + 'sessions'


def display_index(request):
    """
    Display a list of session links (directories)

    Args:
        request:

    Returns:

    """
    template = loader.get_template('tracemap/index.html')
    sessions_dir = get_session_dir()
    sessions = list_sessions(sessions_dir)
    context = {
        'sessions': sessions
    }
    return HttpResponse(template.render(context, request))


def list_view(request):
    files = AudioRecording.objects.all()
    return display_recordings_list(files, request)


def single_view(request, pk):
    files = [AudioRecording.objects.get(id=pk)]
    return display_recordings_list(
        files,
        request,
        {'title': files[0].identifier}
    )


def genus_view(request, genus):
    files = AudioRecording.objects.filter(genus=genus)
    return display_recordings_list(
        files,
        request,
        {'title': f'Genus: {genus}'}
    )


def species_view(request, genus, species):
    files = AudioRecording.objects.filter(genus=genus, species=species)
    return display_recordings_list(
        files,
        request,
        {'title': f'Species: {genus} ({species})'}
    )


def display_recordings_list(files, request, context: dict = None):
    if context is None:
        context = {}
    traces = [audio_for_json(f) for f in files]
    bounds = bounds_from_recordings(files)
    template = loader.get_template('tracemap/list.html')
    local_context = {
        'map_data': {'traces': traces, 'bounds': bounds},
        'mapbox_token': settings.MAPS['mapbox_token'],
    }
    context = {**context, **local_context}
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


def summarise_by_day():
    f_day = lambda d: d.strftime('%Y-%m-%d') if d is not None else None

    # Take all the objects
    # Annotate them with a day record
    # Identify (group) by values
    # Annotate the groups with a count of rows
    # Spit out the summary
    days_by_species = AudioRecording.objects \
        .annotate(day=TruncDay('recorded_at')) \
        .values('day', 'genus', 'species') \
        .annotate(count=Count('id')) \
        .values('day', 'genus', 'species', 'count')

    unique_days = set([f_day(row['day']) for row in days_by_species])
    unique_genus = set([row['genus'] for row in days_by_species])

    days = {day: {'day': day, 'count': 0, 'genus': {g: {} for g in unique_genus}} for day in unique_days}
    genus_map = {g: [] for g in unique_genus}

    for row in days_by_species:
        day_key = f_day(row['day'])
        days[day_key]['count'] += row['count']
        for g in unique_genus:
            if row['genus'] == g:
                days[day_key]['genus'][g][row['species']] = row['count']
                genus_map[g].append(row['species'])

    genus_map = { g: sorted(set(genus_map[g])) for g in genus_map}

    return days, genus_map


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
