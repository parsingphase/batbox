from django.db import models
from batbox import settings
import json
import os


# Create your models here.

class AudioRecording(models.Model):
    identifier = models.CharField(max_length=32, blank=True)
    file = models.FilePathField(
        path=settings.MEDIA_ROOT + 'sessions/',
        recursive=True,
        match=r'^[^.].*\.wav'
    )
    processed = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    genus = models.CharField(max_length=16, blank=True)
    species = models.CharField(max_length=16, blank=True)
    recorder_serial = models.CharField(max_length=16, blank=True)
    guano_data = models.TextField(blank=True)

    def path_relative_to(self, base_dir):
        if self.file is not None:
            return os.path.relpath(self.file, base_dir)
        return None

    def as_serializable(self):
        return {
            'identifier': self.identifier,
            'file': self.file,
            'processed': self.processed,
            'recorded_at': self.recorded_at.isoformat()
            if self.recorded_at is not None else None,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'latlon': (self.latitude, self.longitude)
            if self.latitude is not None and self.longitude is not None
            else None,
            'genus': self.genus,
            'species': self.species,
            'recorder_serial': self.recorder_serial,
            'guano_data': json.loads(self.guano_data),
        }
