from batbox import settings
from datetime import datetime, timedelta, date
from dateutil.parser import parse as parse_date
from django.db.models import Count, Min, Max
from django.db.models.functions import TruncDay
from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
from django.core.exceptions import PermissionDenied
from django.template import loader
from os import path
from tracemap.models import AudioRecording
from svg_calendar import GridImage
from svgwrite.container import Hyperlink
from svgwrite.path import Path
from svgwrite.text import Text
from svgwrite import shapes, Drawing
from typing import List, Tuple
from .repository import SpeciesLookup, NonUniqueSpeciesLookup


def decorate_rect_with_class(rect: shapes.Rect, day: date, _):
    """
    Decorator for day squares for SVG calendar view
    Args:
        rect:
        day:
        _:

    Returns:

    """
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

    # return None
    template = loader.get_template('tracemap/days_index.html')
    summary, genuses = summarise_by_day()
    days = sorted(summary.values(), key=lambda d: d['day'] if d['day'] is not None else '')

    context = {
        'days': days,
        'genuses': genuses,
    }
    return HttpResponse(template.render(context, request))


def calendar(request):
    """
    Create a calendar view recordings

    Args:
        request:

    Returns:

    """
    template = loader.get_template('tracemap/calendar.html')

    counts_by_day = list_counts_by_day()

    grid_image = GridImage().set_day_rect_decorator(decorate_rect_with_class)
    image = grid_image.draw_daily_count_image(counts_by_day, True).tostring()

    context = {
        'calendar_svg': image,
    }
    return HttpResponse(template.render(context, request))


def day(request, date):
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


def list_all(request):
    search_params = request.GET
    if search_params:
        search_filter = build_search_filter(search_params)
        files = AudioRecording.objects.filter(**search_filter)
    else:
        files = AudioRecording.objects.filter(hide=False)
    return display_recordings_list(files, request, {'title': 'All recordings'})


def single(request, pk):
    files = [AudioRecording.objects.get(id=pk)]
    if len(files) == 0:
        raise Http404('Recording not found')

    if files[0].hide:
        raise PermissionDenied('Recording not available')

    return display_recordings_list(
        files,
        request,
        {'title': files[0].identifier}
    )


def genus(request, genus_name):
    files = AudioRecording.objects.filter(genus=genus_name)
    title = f'Genus: {genus_name}'
    genus_latin_name = SpeciesLookup().genus_name_by_abbreviation(genus_name)
    if genus_latin_name is not None and type(genus_latin_name) is not list:
        title += f' ({genus_latin_name})'
    return display_recordings_list(
        files,
        request,
        {'title': title}
    )


def species(request, genus_name, species_name):
    files = AudioRecording.objects.filter(genus=genus_name, species=species_name)
    title_genus_case = genus_name[0].upper() + genus_name[1:].lower()
    title = f'Species: {title_genus_case}. {species_name.lower()}.'
    context = {}
    try:
        species_details = SpeciesLookup().species_by_abbreviations(genus_name, species_name)
        title += f'({species_details.genus} {species_details.species})'
        if species_details.common_name is not None:
            context['subtitle'] = species_details.common_name
    except NonUniqueSpeciesLookup:
        pass
    finally:
        context['title'] = title

    return display_recordings_list(
        files,
        request,
        context
    )


def search(request):
    template = loader.get_template('tracemap/search.html')
    range = AudioRecording.objects.all().aggregate(min=Min('recorded_at'), max=Max('recorded_at'))
    range = {k: t.strftime('%Y-%m-%d') if t else None for k, t in range.items()}

    _, genii = summarise_by_day()
    context = {
        'genii': genii,
        'date_range': range,
        'mapbox_token': settings.MAPS['mapbox_token'],
    }
    return HttpResponse(template.render(context, request))


def display_recordings_list(files: List[AudioRecording], request, context: dict = None):
    """
    Generate page view based on list of files passed
    Args:
        files:
        request:
        context:

    Returns:

    """
    if context is None:
        context = {}

    lookup = SpeciesLookup()
    traces = []
    for f in files:
        trace = f.as_serializable()
        trace['url'] = settings.MEDIA_URL + path.relpath(trace['file'], settings.MEDIA_ROOT)
        trace['file'] = None
        try:
            species_info = lookup.species_by_abbreviations(f.genus, f.species)
        except NonUniqueSpeciesLookup:
            species_info = None
        trace['species_info'] = species_info.as_serializable() if species_info else ''
        traces.append(trace)

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


def list_counts_by_day():
    days = AudioRecording.objects \
        .filter(hide=False) \
        .annotate(day=TruncDay('recorded_at')) \
        .values('day').annotate(c=Count('id')) \
        .values('day', 'c').order_by('day')

    days = {day['day'].strftime('%Y-%m-%d'): day['c'] for day in days if day['day'] is not None}

    return days


def summarise_by_day() -> Tuple[dict, dict]:
    """
    Generate a list of all genus, and the species within, alongside the number of recordings per species
    Returns:

    """

    def f_day(d):
        return d.strftime('%Y-%m-%d') if d is not None else None

    # Take all the objects
    # Annotate them with a day record
    # Identify (group) by values
    # Annotate the groups with a count of rows
    # Spit out the summary
    days_by_species = AudioRecording.objects \
        .filter(hide=False) \
        .annotate(day=TruncDay('recorded_at')) \
        .values('day', 'genus', 'species') \
        .annotate(count=Count('id')) \
        .values('day', 'genus', 'species', 'count')

    unique_days = set([f_day(row['day']) for row in days_by_species])
    unique_genus = set([row['genus'] for row in days_by_species])

    days = {day: {'day': day, 'count': 0, 'genus': {g: {} for g in unique_genus}} for day in unique_days}
    genus_species = {g: [] for g in unique_genus}

    for row in days_by_species:
        day_key = f_day(row['day'])
        days[day_key]['count'] += row['count']
        for genus_abbr in unique_genus:
            if row['genus'] == genus_abbr:
                days[day_key]['genus'][genus_abbr][row['species']] = row['count']
                genus_species[genus_abbr].append(row['species'])

    lookup = SpeciesLookup()
    gl = lookup.genus_name_by_abbreviation
    # genus_species = Map of (eg) { PYP: [NAT, PIP, PYG], …} - species lists are unsorted here

    genus_map = {}
    for genus_abbr in genus_species:
        name = gl(genus_abbr)
        genus_map[genus_abbr] = {
            'name': name if type(name) is str else None,
            'species': []
        }
        species_abbreviations = sorted(set(genus_species[genus_abbr]))

        for species_abbr in species_abbreviations:
            try:
                species_data = lookup.species_by_abbreviations(genus_abbr, species_abbr)
            except NonUniqueSpeciesLookup:
                species_data = None

            species_item = {
                'abbreviation': species_abbr,
                'species': species_data
            }
            genus_map[genus_abbr]['species'].append(species_item)

    return days, genus_map


def search_api(request: HttpRequest):
    search_params = request.GET
    search_filter = build_search_filter(search_params)

    results = AudioRecording.objects.filter(**search_filter)
    results = [{'lat': f.latitude, 'lng': f.longitude, 'value': 1} for f in results]
    return JsonResponse({'data': results, 'search': search_filter}, safe=False)


def build_search_filter(search_params):
    search_filter = {
        'hide': False
    }
    if 'species' in search_params:
        search_filter['species__in'] = search_params['species'].split(',')
    if 'west' in search_params:
        search_filter['longitude__gte'] = search_params['west']
    if 'east' in search_params:
        search_filter['longitude__lte'] = search_params['east']
    if 'south' in search_params:
        search_filter['latitude__gte'] = search_params['south']
    if 'north' in search_params:
        search_filter['latitude__lte'] = search_params['north']
    if 'start' in search_params:
        search_filter['recorded_at__gte'] = parse_date(search_params['start'])
    if 'end' in search_params:
        search_filter['recorded_at__lte'] = parse_date(search_params['end'])
    return search_filter


def species_marker(request, genus_name='-', species_name='-'):
    if species_name == '-':
        color = 'bbbbbb'
        species_name = '?'
    else:
        color = species_to_color(genus_name, species_name)

    marker_width = 60
    marker_height = 100
    marker_border = 5
    stroke_width = 1
    line_color = 'black'
    marker_color = '#' + color
    bezier_length = marker_width / 3

    width = marker_width + marker_border * 2
    height = marker_height + marker_border * 2
    font_size = marker_height / 4

    arc_centre_drop = (marker_height / 3.5)  # Distance from top of marker to rotation centre
    arc_radius_vertical = arc_centre_drop

    image = Drawing(size=('%dpx' % width, '%dpx' % height))
    # image.add(image.rect((0, 0), (width, height), fill='red'))
    path = Path(stroke=line_color, stroke_width=stroke_width, fill=marker_color)

    path.push(f'M {marker_border} {arc_centre_drop + marker_border} ')  # Left arc edge

    path.push(
        f'C {marker_border}  {arc_centre_drop + marker_border + bezier_length} '  # Left edge + vrt bez
        f'{width / 2 - bezier_length / 3} {height - marker_border - bezier_length} '  # Point - (b/3) h, - b v
        f'{width / 2} {height - marker_border}'  # Point
    )

    path.push(
        f'C {width / 2 + bezier_length / 3} {height - marker_border - bezier_length} '  # Point + b/3 h, -b v
        f'{width - marker_border} {arc_centre_drop + marker_border + bezier_length} '  # Right edge + vrt bez
        f'{width - marker_border} {arc_centre_drop + marker_border} '  # Right edge

    )  # Right arc edge

    path.push_arc(target=(marker_border, arc_centre_drop + marker_border), rotation=180,
                  r=(marker_width / 2, arc_radius_vertical), absolute=True, angle_dir='-')

    path.push('z')
    image.add(path)
    image.add(
        Text(species_name, (width / 2, marker_border + arc_centre_drop + marker_height / 20), font_family='Arial',
             font_size=font_size, dominant_baseline="middle", text_anchor="middle")
    )

    return HttpResponse(image.tostring(), content_type='image/svg+xml')


def species_to_color(genus_part: str, species_part: str):
    def char_to_num(char):
        return ord(char.upper()) - ord('A')

    genus_part = genus_part.ljust(3, 'X')
    species_part = species_part.ljust(3, 'X')

    color = ''
    for i in range(0, 3):
        channel = 80 + (6 * char_to_num(genus_part[i])) + char_to_num(species_part[i])
        color += hex(channel)[2:].zfill(2)

    return color
