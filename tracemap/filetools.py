import re
from datetime import datetime
from typing import List
from tracemap.datatypes import Point

import xmltodict


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


class KmlParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def get_recording_points(self) -> List[Point]:
        with open(self.filepath) as fd:
            kml = xmltodict.parse(fd.read())['kml']['Document']
            # map_data['styles'] = kml['Style']
            # Two types of placemark: containing Point or LineString
            points = [self.xml_dict_to_point(p) for p in kml['Placemark'] if 'Point' in p]

            return points

    def xml_dict_to_point(self, data: dict) -> Point:
        point = Point()
        point.description = data['description']
        point.id = data['name']
        point.style = data['styleUrl']
        (point.lon, point.lat, _altitude) = data['Point']['coordinates'].split(',')
        return point
