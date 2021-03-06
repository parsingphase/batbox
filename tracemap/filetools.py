"""
Tools to help with file parsing
"""
import re
from datetime import datetime
from typing import List

import xmltodict

from tracemap.datatypes import Point


def xml_dict_to_point(data: dict) -> Point:
    """
    Create a Point from a dict representing a location in KML

    Args:
        data: xml dict data

    Returns:
        Point
    """
    point = Point()
    point.description = data['description']
    point.name = data['name']
    point.style = data['styleUrl']
    (point.lon, point.lat, _) = data['Point']['coordinates'].split(',')
    return point


class TraceIdentifier:
    """
    Tool to generate basic metadata from a filename
    eg PIPPIP_20190430_210112
    or 20150610_215446
    String should exclude filetype
    """

    # pylint: disable=R0903

    def __init__(self, identifier_string):
        self.matched = False
        self.identified = False
        self.species = None
        self.genus = None
        self.datetime = None
        self.identifier_string = identifier_string
        match = re.match(
            r'^((((?P<genus>\w{3})(?P<species>\w{3}))|(No_?ID)|(NOISE))_)?'
            r'(?P<date>\d{8})_(?P<time>\d{6})$',
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
            if fields['genus']:
                self.identified = True
                self.genus = fields['genus']
                self.species = fields['species']

    def as_dict(self):
        """
        Return data as a dictionary, eg for serialization
        """
        return {
            'matched': self.matched,
            'identified': self.identified,
            'species': self.species,
            'genus': self.genus,
            'datetime': self.datetime,
        }


class KmlParser:
    """
    Parses a KML file
    """

    # pylint: disable=R0903
    def __init__(self, filepath):
        self.filepath = filepath

    def get_recording_points(self) -> List[Point]:
        """
        Extract all the recording locations from this file
        Returns:
            List of Point objects
        """
        with open(self.filepath) as file:
            kml = xmltodict.parse(file.read())['kml']['Document']
            # map_data['styles'] = kml['Style']
            # Two types of placemark: containing Point or LineString
            points = [
                xml_dict_to_point(p) for p in kml['Placemark']
                if 'Point' in p
            ]

            return points
