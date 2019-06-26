import json
import os

from django.db import models

from batbox import settings


# Create your models here.

class AudioRecording(models.Model):
    identifier = models.CharField(max_length=32, blank=True)
    audio_file = models.FilePathField(
        path=settings.MEDIA_ROOT + 'sessions/',
        recursive=True,
        match=r'^[^.].*\.wav'
    )
    subsampled_audio_file = models.FilePathField(
        path=settings.MEDIA_ROOT + 'processed/subsampled/',
        recursive=True,
        match=r'^[^.].*\.wav',
        null=True,
        blank=True
    )
    spectrogram_image_file = models.FilePathField(
        path=settings.MEDIA_ROOT + 'processed/spectrograms/',
        recursive=True,
        match=r'^[^.].*\.png',
        null=True,
        blank=True
    )
    processed = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    genus = models.CharField(max_length=16, blank=True)
    species = models.CharField(max_length=16, blank=True)
    recorder_serial = models.CharField(max_length=16, blank=True)
    guano_data = models.TextField(blank=True)
    duration = models.FloatField(blank=True, null=True)
    hide = models.BooleanField(default=False)  # Allow to ignore files not containing useful recordings

    def path_relative_to(self, base_dir):
        if self.audio_file is not None:
            return os.path.relpath(self.audio_file, base_dir)
        return None

    def as_serializable(self):
        return {
            'id': self.id,
            'identifier': self.identifier,
            'file': self.audio_file,
            'lo_file': self.subsampled_audio_file,
            'spectrogram_file': self.spectrogram_image_file,
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
            'guano_data': json.loads(self.guano_data) if self.guano_data
            else None,
            'duration': self.duration
        }


class Species(models.Model):
    genus = models.CharField(max_length=32, blank=True)
    species = models.CharField(max_length=32, blank=True)
    common_name = models.CharField(max_length=64, blank=True)
    canon_genus_3code = models.CharField(max_length=3, blank=True)
    canon_6code = models.CharField(max_length=6, blank=True)
    mdd_id = models.IntegerField(null=True)

    def __setitem__(self, key, value):
        if key in ['genus', 'species', 'common_name', 'canon_genus_3code', 'canon_6code', 'mdd_id']:
            setattr(self, key, value)
        else:
            raise Exception(f'Key "{key}" cannot be set dynamically')

    class Meta:
        verbose_name = 'Species'
        verbose_name_plural = 'Species'

    def as_serializable(self):
        return {
            'id': self.id,
            'genus': self.genus,
            'species': self.species,
            'common_name': self.common_name,
            'mdd_id': self.mdd_id,
        }
