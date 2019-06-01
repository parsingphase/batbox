from django.db import models
from batbox import settings


# Create your models here.

class AudioRecording(models.Model):
    identifier = models.CharField(max_length=32, blank=True)
    file = models.FilePathField(path=settings.MEDIA_ROOT + 'sessions/', recursive=True, match=r'^[^.].*\.wav')
    processed = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    genus = models.CharField(max_length=16, blank=True)
    species = models.CharField(max_length=16, blank=True)
    recorder_serial = models.CharField(max_length=16, blank=True)
    guano_data = models.TextField(blank=True)
