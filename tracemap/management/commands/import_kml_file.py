from django.core.management.base import BaseCommand
from tracemap.models import AudioRecording
from tracemap.filetools import KmlParser


class Command(BaseCommand):
    help = 'Load a kml file to update recordings in database'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename', type=str, help='Name of the file to import'
        )

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        print(f'Loading KML fron {filename}')
        parser = KmlParser(filename)
        points = parser.get_recording_points()
        for point in points:
            ident = point.id
            audio_files = AudioRecording.objects.filter(identifier=ident)
            if len(audio_files) == 1:
                audio = audio_files[0]  # type: AudioRecording
                if audio.processed is False:
                    audio.latitude = point.lat
                    audio.longitude = point.lon
                    audio.processed = True
                    audio.save()
                    print(f'Added location to {ident}')
                else:
                    print(f'Already had location for {ident}')

            elif len(audio_files) > 1:
                print(f'More than one match for {ident}, skipping')
