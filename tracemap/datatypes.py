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


def bound_from_points(points: list):
    min_lat = min([p.lat for p in points])
    min_lon = min([p.lon for p in points])
    max_lat = max([p.lat for p in points])
    max_lon = max([p.lon for p in points])
    return (min_lat, min_lon), (max_lat, max_lon)
