"""
Custom data types use by tracemap
"""


class Point:
    """
    Data holder for lat/lon data from a guano import
    """

    def __init__(  # pylint: disable=R0913
            self, name=None, lat=None, lon=None, description=None, style=None
    ):
        self.name = name
        self.description = description
        self.style = style
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return repr(self.as_dict())

    def as_dict(self):
        """
        Return data in a dictionary, eg for serialization
        """
        return {
            'name': self.name,
            'description': self.description,
            'style': self.description,
            'position': (self.lat, self.lon)
        }
