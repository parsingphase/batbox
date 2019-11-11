"""
Django entity models for bat recording data
"""
import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

from django.db import models

from batbox import settings


class AudioRecording(models.Model):
    """
    Entity representing an audio recording file
    """
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
    recorded_at_utc = models.DateTimeField(null=True, blank=True)
    recorded_at_iso = models.CharField(max_length=30, null=True, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    genus = models.CharField(max_length=16, blank=True)
    species = models.CharField(max_length=16, blank=True)
    recorder_serial = models.CharField(max_length=16, blank=True)
    guano_data = models.TextField(blank=True)
    duration = models.FloatField(blank=True, null=True)
    hide = models.BooleanField(default=False)  # Ignore files not containing useful recordings

    def path_relative_to(self, base_dir: str) -> Optional[str]:
        """
        Helper function to subtract a base directory from a path
        Args:
            base_dir: Base directory to remove

        Returns:
            Relative path
        """
        if self.audio_file is not None:
            return os.path.relpath(self.audio_file, base_dir)
        return None

    def as_serializable(self) -> Dict:
        """
        Return object data in a format that can be json-serialized
        Returns:
            Dictionary of data
        """
        if self.latitude is not None and self.longitude is not None:
            lat_lon = (self.latitude, self.longitude)
        else:
            lat_lon = None
        return {
            'id': self.id,
            'identifier': self.identifier,
            'file': self.audio_file,
            'lo_file': self.subsampled_audio_file,
            'spectrogram_file': self.spectrogram_image_file,
            'processed': self.processed,
            'recorded_at': self.recorded_at_iso,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'latlon': lat_lon,
            'genus': self.genus,
            'species': self.species,
            'recorder_serial': self.recorder_serial,
            'guano_data': json.loads(self.guano_data) if self.guano_data else None,
            'duration': self.duration
        }

    def set_recording_time(self, recording_time: datetime):
        """
        Set recording time in human-readable and timezone-aware formats
        Args:
            recording_time: datetime recording time

        Returns:
            void
        """
        self.recorded_at_utc = recording_time.astimezone(timezone.utc)
        self.recorded_at_iso = recording_time.isoformat()


class Species(models.Model):
    """
    Entity representing a single species of bat
    """
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

    def as_serializable(self) -> Dict:
        """
        Return object data in a format that can be json-serialized
        Returns:
            Dictionary of data
        """
        return {
            'id': self.id,
            'genus': self.genus,
            'species': self.species,
            'common_name': self.common_name,
            'mdd_id': self.mdd_id,
        }
