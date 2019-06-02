from django.core.management.base import BaseCommand
from tracemap.models import AudioRecording
import os
from tracemap.filetools import TraceIdentifier
from guano import GuanoFile
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Load an audio file into database'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename', type=str, help='Name of the file to import'
        )

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']

        if os.path.isfile(filename):
            filepath = os.path.realpath(filename)
            filestem = os.path.basename(filename).split('.')[0]
            print(f'Loading {filepath}')

            existing_audio = AudioRecording.objects.filter(file=filepath)
            if len(existing_audio):
                audio = existing_audio[0]
                audio.identifier = filestem
                if audio.processed:
                    print("Already processed this file, skipping")
                    return
                print('Found incomplete existing record, trying to update')
            else:
                audio = AudioRecording(file=filepath, identifier=filestem)

            id_parser = TraceIdentifier(filestem)
            if id_parser.matched:
                audio.recorded_at = id_parser.datetime

            if id_parser.genus:
                audio.genus = id_parser.genus

            if id_parser.species:
                audio.species = id_parser.species

            try:
                guano_file = GuanoFile(filepath)
            except:  # noqa:E722 FIXME
                print(f'Unable to load guano data for {filename}')
                audio.save()
                return

            guano_dict = {k: v for k, v in guano_file.items()}

            for k, v in guano_dict.items():
                if isinstance(v, datetime):
                    guano_dict[k] = v.strftime('%Y-%m-%d %H:%M:%S')

            audio.guano_data = json.dumps(guano_dict)
            if 'Loc Position' in guano_dict:
                audio.latitude, audio.longitude = guano_dict['Loc Position']

            if 'Serial' in guano_file:
                audio.recorder_serial = guano_file['Serial']

            try:
                if 'Timestamp' in guano_file \
                        and guano_file['Timestamp'] is not None:
                    if guano_file['Timestamp'].utcoffset() is None:
                        print(
                            'Timestamp with no tzinfo from guano '
                            'cannot be saved'
                        )
                    else:
                        audio.recorded_at = guano_file['Timestamp']
            except ValueError:
                print('Cannot use timestamp from guano - no valid TZ?')

            audio.save()
        else:
            print(f'{filename} not found')
