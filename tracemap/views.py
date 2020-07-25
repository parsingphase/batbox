"""
Module views, responding to routed URLs
"""
# pylint: disable=R0914
# - Can't modify number of views - can we refactor to class?
from datetime import date, datetime, timedelta
from os import path
from typing import List, Tuple

from dateutil.parser import parse as parse_date
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Max, Min
from django.db.models.functions import Substr
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.template import loader, response
from svgwrite import Drawing, shapes
from svgwrite.container import Hyperlink
from svgwrite.path import Path
from svgwrite.text import Text

from batbox import settings
from svg_calendar import GridImage
from tracemap.models import AudioRecording

from .repository import NonUniqueSpeciesLookup, SpeciesLookup


def decorate_rect_with_class(rect: shapes.Rect, day_date: date, _):
    """
    Decorator for day squares for SVG calendar view
    Args:
        rect:
        day_date:
        _:

    Returns:

    """
    day_string = day_date.strftime('%Y-%m-%d')
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


def day(request, date_string):
    """
    Render list+map view for a single day
    Args:
        request:
        date_string: date in yyyy-mm-dd format

    Returns:
        HTTP response containing formatted output
    """
    if date_string == 'undated':
        files = AudioRecording.objects.filter(recorded_at__isnull=True, hide=False)
    else:
        (year, month, day_number) = date_string.split('-')
        date_start = datetime(int(year), int(month), int(day_number))
        date_end = date_start + timedelta(days=1)
        files = AudioRecording.objects.filter(
            recorded_at_iso__gte=date_start.isoformat(),
            recorded_at_iso__lte=date_end.isoformat(),
            hide=False
        )

    if len(files) == 0:
        raise Http404("No records")

    context = {
        'title': f'Date: {date_string}',
        'og_title': f'Bat echolocation recordings from {date_string}',
        'og_description': f'Visualisation, location and playback'
    }
    return display_recordings_list(files, request, context)


def list_all(request):
    """
    Render list view for all recordings
    Args:
        request:

    Returns:
        HTTP response containing formatted output
    """
    title = 'All recordings'
    search_params = request.GET
    if search_params:
        search_filter = build_search_filter(search_params)
        files = AudioRecording.objects.filter(**search_filter)
        title = 'Search results'
    else:
        files = AudioRecording.objects.filter(hide=False)
    return display_recordings_list(files, request, {'title': title})


def single(request, primary_key):
    """
    Render list+map view for a single recording
    Args:
        request:
        primary_key: ID of recording

    Returns:
        HTTP response containing formatted output
    """
    files = [AudioRecording.objects.get(id=primary_key)]
    if len(files) == 0:
        raise Http404('Recording not found')

    file = files[0]  # type: AudioRecording

    if file.hide:
        raise PermissionDenied('Recording not available')

    context = {
        'title': file.identifier,
        'og_description': f'Visualisation, location and playback'
    }

    species_details = SpeciesLookup().species_by_abbreviations(file.genus, file.species)

    if species_details:
        when = parse_date(file.recorded_at_iso).strftime('%Y-%m-%d %H:%M')
        species = title_case(species_details.species)
        context['og_title'] = f'{species_details.common_name} ({species_details.genus} {species}) recording from {when}'

    return display_recordings_list(
        files,
        request,
        context
    )


def genus(request, genus_name):
    """
    Render list+map view for a single genus
    Args:
        request:
        genus_name: Genus name abbreviation

    Returns:
        HTTP response containing formatted output
    """
    files = AudioRecording.objects.filter(genus=genus_name, hide=False)
    title = f'Genus: {genus_name}'
    safe_genus_name = genus_name

    genus_latin_name = SpeciesLookup().genus_name_by_abbreviation(genus_name)

    if genus_latin_name is not None and not isinstance(genus_latin_name, list):
        title += f' ({genus_latin_name})'
        safe_genus_name = genus_latin_name

    context = {
        'title': title,
        'og_title': f'Bat echolocation recordings from {safe_genus_name}',
        'og_description': f'Visualisation, location and playback'
    }

    return display_recordings_list(
        files,
        request,
        context
    )


def species(request, genus_name, species_name):
    """
    Render list+map view for a single genus
    Args:
        request:
        genus_name: Genus name abbreviation
        species_name: Species name abbreviation

    Returns:
        HTTP response containing formatted output
    """
    files = AudioRecording.objects.filter(genus=genus_name, species=species_name, hide=False)
    title_genus_case = title_case(genus_name)
    safe_latin_name = f'{title_genus_case}. {species_name.lower()}.'
    safe_common_name = None

    title = f'Species: {safe_latin_name}'
    context = {
        'og_description': f'Visualisation, location and playback'
    }
    try:
        species_details = SpeciesLookup().species_by_abbreviations(genus_name, species_name)
        if species_details:
            safe_latin_name = f'{species_details.genus} {species_details.species}'
            title += f' ({safe_latin_name})'
            if species_details.common_name is not None:
                safe_common_name = species_details.common_name
                context['subtitle'] = safe_common_name
    except NonUniqueSpeciesLookup:
        pass
    finally:
        context['title'] = title

    safe_species_name = f'{safe_common_name} ({safe_latin_name})' if safe_common_name else safe_latin_name

    context['og_title'] = f'Bat echolocation recordings from {safe_species_name}'

    return display_recordings_list(
        files,
        request,
        context
    )


def title_case(in_string):
    return in_string[0].upper() + in_string[1:].lower()


def search(request):
    """
    Generate the search view
    Args:
        request:

    Returns:

    """
    template = loader.get_template('tracemap/search.html')
    time_range = AudioRecording.objects.all(). \
        aggregate(min=Min('recorded_at_iso'), max=Max('recorded_at_iso'))

    # Clip from start to end of day
    time_range = {
        'min': parse_date(time_range['min']).strftime('%Y-%m-%d'),
        'max': (parse_date(time_range['max']) + timedelta(days=1)).strftime('%Y-%m-%d'),
    }

    default_range = {
        'center': [55, 0],
        'zoom': 4
    }

    _, genii = summarise_by_day()
    context = {
        'genii': genii,
        'date_range': time_range,
        'mapbox_token': settings.MAPS['mapbox_token'],
        'search_defaults': settings.MAPS['search_defaults'] if 'search_defaults' in settings.MAPS else default_range
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
    urls_map = {
        'file': 'url',
        'lo_file': 'lo_url',
        'spectrogram_file': 'spectrogram_url',
    }

    for file in files:
        trace = file.as_serializable()
        for file_key, url_key in urls_map.items():
            if trace[file_key]:
                tracefile = trace[file_key]
                trace[url_key] = media_path_to_relative_url(tracefile)
            trace[file_key] = None

        try:
            species_info = lookup.species_by_abbreviations(file.genus, file.species)
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

    og_context = {}

    files_with_spectrogram = [x for x in traces if x['spectrogram_url']]
    if len(files_with_spectrogram):
        first_file = files_with_spectrogram[0]
        print(first_file)
        og_context['og_image'] = f'{request.scheme}://{request.get_host()}{first_file["spectrogram_url"]}'
        if first_file['spectrogram_width']:
            og_context['og_image_width'] = first_file['spectrogram_width']
            og_context['og_image_height'] = first_file['spectrogram_height']

    context = {**context, **og_context, **local_context}
    return HttpResponse(template.render(context, request))


def media_path_to_relative_url(tracefile):
    """
    Handle path matching, whether there's a symlink in the stored or actual path
    Args:
        tracefile:

    Returns:

    """
    relpath = path.relpath(tracefile, settings.MEDIA_ROOT)
    if '..' in relpath:
        relpath = path.relpath(path.realpath(tracefile), settings.MEDIA_ROOT)
    return settings.MEDIA_URL + relpath


def bounds_from_recordings(files: List[AudioRecording]) -> Tuple:
    """
    Generate map bounds from a list of recordings
    Args:
        files:

    Returns:

    """
    positioned_files = [f for f in files if f.latitude is not None]
    if positioned_files:
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
    """
    Generate a count of records by day
    Returns:

    """
    days = AudioRecording.objects \
        .filter(hide=False) \
        .annotate(day=Substr('recorded_at_iso', 1, 10)) \
        .values('day').annotate(c=Count('id')) \
        .values('day', 'c').order_by('day')

    days = {day['day'][0:10]: day['c'] for day in days if day['day'] is not None}

    return days


def summarise_by_day() -> Tuple[dict, dict]:
    """
    Generate a list of all genus, and the species within, plus number of recordings per species
    Returns:

    """

    def f_day(date_string):
        return parse_date(date_string).strftime('%Y-%m-%d') if date_string is not None else None

    # Take all the objects
    # Annotate them with a day record
    # Identify (group) by values
    # Annotate the groups with a count of rows
    # Spit out the summary
    days_by_species = AudioRecording.objects \
        .filter(hide=False) \
        .annotate(day=Substr('recorded_at_iso', 1, 10)) \
        .values('day', 'genus', 'species') \
        .annotate(count=Count('id')) \
        .values('day', 'genus', 'species', 'count')

    # FIXME:  R1718: Consider using a set comprehension (consider-using-set-comprehension)
    # pylint: disable=R1718
    unique_days = set([f_day(row['day']) for row in days_by_species])
    unique_genus = set([row['genus'] for row in days_by_species])

    days = {
        day: {'day': day, 'count': 0, 'genus': {g: {} for g in unique_genus}}
        for day in unique_days
    }

    genus_species = {g: [] for g in unique_genus}

    for row in days_by_species:
        day_key = f_day(row['day'])
        days[day_key]['count'] += row['count']
        for genus_abbr in unique_genus:
            if row['genus'] == genus_abbr:
                days[day_key]['genus'][genus_abbr][row['species']] = row['count']
                genus_species[genus_abbr].append(row['species'])

    lookup = SpeciesLookup()
    genus_lookup = lookup.genus_name_by_abbreviation
    # genus_species = Map of (eg) { PYP: [NAT, PIP, PYG], …} - species lists are unsorted here

    genus_map = {}
    for genus_abbr in genus_species:
        name = genus_lookup(genus_abbr)
        genus_map[genus_abbr] = {
            'name': name if isinstance(name, str) else None,
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
    """
    API call handler for search
    Args:
        request:

    Returns:

    """
    search_params = request.GET
    search_filter = build_search_filter(search_params)

    results = AudioRecording.objects.filter(**search_filter)
    results = [{'lat': f.latitude, 'lng': f.longitude, 'value': 1} for f in results]
    return JsonResponse({'data': results, 'search': search_filter}, safe=False)


def build_search_filter(search_params: dict):
    """
    Build a search filter for the django ORM from a dictionary of query params

    Args:
        search_params:

    Returns:

    """
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
        search_filter['recorded_at_iso__gte'] = search_params['start']
    if 'end' in search_params:
        search_filter['recorded_at_iso__lte'] = search_params['end']
    return search_filter


def species_marker(request, genus_name='-', species_name='-'):
    """
    Generate a SVG marker for a given species
    Args:
        request:
        genus_name:
        species_name:

    Returns:

    """
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
    marker = Path(stroke=line_color, stroke_width=stroke_width, fill=marker_color)

    marker.push(f'M {marker_border} {arc_centre_drop + marker_border} ')  # Left arc edge

    marker.push(
        f'C {marker_border} {arc_centre_drop + marker_border + bezier_length} '
        f'{width / 2 - bezier_length / 3} {height - marker_border - bezier_length} '
        f'{width / 2} {height - marker_border}'  # Point
    )

    marker.push(
        f'C {width / 2 + bezier_length / 3} {height - marker_border - bezier_length} '
        f'{width - marker_border} {arc_centre_drop + marker_border + bezier_length} '
        f'{width - marker_border} {arc_centre_drop + marker_border} '  # Right edge
    )  # Right arc edge

    marker.push_arc(
        target=(marker_border, arc_centre_drop + marker_border),
        rotation=180,
        r=(marker_width / 2, arc_radius_vertical),
        absolute=True,
        angle_dir='-'
    )

    marker.push('z')
    image.add(marker)
    image.add(
        Text(species_name, (width / 2, marker_border + arc_centre_drop + marker_height / 20),
             font_family='Arial',
             font_size=font_size, dominant_baseline="middle", text_anchor="middle")
    )

    return HttpResponse(image.tostring(), content_type='image/svg+xml')


def species_to_color(genus_part: str, species_part: str):
    """
    Create a unique-ish color from a species name
    Species from same genus will be more similar

    Args:
        genus_part:
        species_part:

    Returns:

    """

    def char_to_num(char):
        return ord(char.upper()) - ord('A')

    genus_part = genus_part.ljust(3, 'X')
    species_part = species_part.ljust(3, 'X')

    color = ''
    for i in range(0, 3):
        channel = 80 + (6 * char_to_num(genus_part[i])) + char_to_num(species_part[i])
        color += hex(channel)[2:].zfill(2)

    return color


def about(request):
    """
    Render the "about" page
    Args:
        request:

    Returns:

    """
    return response.SimpleTemplateResponse('tracemap/about.html')
