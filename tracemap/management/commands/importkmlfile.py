from django.core.management.base import BaseCommand
from tracemap.models import AudioRecording
from tracemap.filetools import KmlParser
from glob import glob
import os


class Command(BaseCommand):
    help = 'Load position data from kml files to update recordings in database'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Name of the file or directory to import')
        parser.add_argument(
            '-r', '--recursive', action='store_true', help='Recurse in directory, finding all .kml files'
        )

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        recurse = kwargs['recursive']

        if os.path.isfile(filename):
            self.process_file(filename)
        elif os.path.isdir(filename):
            if recurse:
                target = filename + '/**/*.[kK][mM][lL]'
            else:
                target = filename + '/*.[kK][mM][lL]'

            files = glob(target, recursive=recurse)
            for file in files:
                print(file)
                self.process_file(file)
            if not files:
                print('Found no files')
        else:
            print(f'{filename} not found')
            exit(1)

    @staticmethod
    def process_file(filename):
        print(f'Loading KML from {filename}')
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
