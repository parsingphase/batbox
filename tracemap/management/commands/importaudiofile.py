from django.core.management.base import BaseCommand
from tracemap.models import AudioRecording
import os
from tracemap.filetools import TraceIdentifier
from guano import GuanoFile
from wamd import WamdFile
from glob import glob
import json
from datetime import datetime
import audioread


def populate_audio_identification(audio: AudioRecording, raw_ident: str):
    if len(raw_ident) == 6:
        audio.species = raw_ident[0:3]
        audio.genus = raw_ident[3:6]
    elif len(raw_ident) == 4:
        audio.species = raw_ident[0:2]
        audio.genus = raw_ident[2:4]
    else:
        raise ValueError(f'Identification must be 4 or 6 characters, got "{raw_ident}"')


class Command(BaseCommand):
    help = 'Load audio files into database'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Name of the file or directory to import')
        parser.add_argument(
            '-r', '--recursive', action='store_true', help='Recurse in directory, finding all .wav files'
        )

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        recurse = kwargs['recursive']

        if os.path.isfile(filename):
            self.process_file(filename)
        elif os.path.isdir(filename):
            if recurse:
                target = filename + '/**/*.[wW][aA][vV]'
            else:
                target = filename + '/*.[wW][aA][vV]'

            files = glob(target, recursive=recurse)
            for file in files:
                print(file)
                self.process_file(file)
            if not files:
                print('Found no files')

        else:
            print(f'{filename} not found')
            exit(1)

    def process_file(self, filename):
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

        self.populate_audio_from_identifier(audio)

        try:
            # print(f'Looking for GUANO data for {filename}')
            guano_file = GuanoFile(filepath)
        except ValueError:
            print(f'Unable to load GUANO data for {filename}')
            guano_file = None

        wamd_file = None
        if guano_file is not None:
            self.populate_audio_from_guano(audio, guano_file)
        else:
            # print(f'Looking for WAMD data for {filename}')
            try:
                wamd_file = WamdFile(filepath)
                # print(f'Loaded WAMD data for {filename}')
            except ValueError:
                print(f'Unable to load WAMD data for {filename}')

        if wamd_file is not None:
            self.populate_audio_from_wamd(audio, wamd_file)

        if not audio.duration:
            self.read_file_duration(filename, audio)

        audio.save()

    @staticmethod
    def populate_audio_from_guano(audio: AudioRecording, guano_file: GuanoFile):
        guano_dict = {k: v for k, v in guano_file.items()}
        for k, v in guano_dict.items():
            if isinstance(v, datetime):
                guano_dict[k] = v.strftime('%Y-%m-%d %H:%M:%S')
        audio.guano_data = json.dumps(guano_dict)

        # Species Auto ID: PIPPYG
        # Species Manual ID:
        if 'Species Manual ID' in guano_dict and len(guano_dict['Species Manual ID']) > 0:
            populate_audio_identification(audio, guano_dict['Species Manual ID'])
        elif 'Species Auto ID' in guano_dict and len(guano_dict['Species Auto ID']) > 0:
            populate_audio_identification(audio, guano_dict['Species Auto ID'])

        if 'Loc Position' in guano_dict:
            audio.latitude, audio.longitude = guano_dict['Loc Position']
        if 'Serial' in guano_file:
            audio.recorder_serial = guano_file['Serial']
        if 'Length' in guano_file:
            audio.duration = guano_file['Length']
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
        finally:
            audio.processed = True

    @staticmethod
    def populate_audio_from_identifier(audio):
        id_parser = TraceIdentifier(audio.identifier)
        if id_parser.matched:
            audio.recorded_at = id_parser.datetime
        if id_parser.genus:
            audio.genus = id_parser.genus
        if id_parser.species:
            audio.species = id_parser.species

    @staticmethod
    def read_file_duration(filename, audio):
        with audioread.audio_open(filename) as f:
            audio.duration = f.duration

    @staticmethod
    def populate_audio_from_wamd(audio: AudioRecording, wamd_file: WamdFile):
        if 'serial' in wamd_file:
            audio.recorder_serial = wamd_file['serial']
        if 'gpsfirst' in wamd_file:
            audio.latitude = wamd_file['gpsfirst'][0]
            audio.longitude = wamd_file['gpsfirst'][1]
        if 'manual_id' in wamd_file and len(wamd_file['manual_id']) > 0:
            populate_audio_identification(audio, wamd_file['manual_id'])
        elif 'auto_id' in wamd_file and len(wamd_file['auto_id']) > 0:
            populate_audio_identification(audio, wamd_file['auto_id'])

        audio.processed = True
