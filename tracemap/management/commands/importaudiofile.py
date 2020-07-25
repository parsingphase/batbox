import json
import os
import subprocess
from datetime import datetime
from glob import glob

import audioread
from dateutil import parser as date_parser
from django.core.management.base import BaseCommand
from guano import GuanoFile
from png import Reader

from batbox import settings
from tracemap.filetools import TraceIdentifier
from tracemap.models import AudioRecording
from tracemap.repository import NonUniqueSpeciesLookup, SpeciesLookup
from wamd import WamdFile


def populate_audio_identification(audio: AudioRecording, raw_ident: str):
    if len(raw_ident) == 6:
        audio.genus = raw_ident[0:3]
        audio.species = raw_ident[3:6]
    elif len(raw_ident) == 4:
        audio.genus = raw_ident[0:2]
        audio.species = raw_ident[2:4]
    else:
        print(f'Identification must be 4 or 6 characters, got "{raw_ident}"')
    #     raise ValueError(f'Identification must be 4 or 6 characters, got "{raw_ident}"')
    # Got values like 'No ID' here…


class Command(BaseCommand):
    help = 'Load audio files into database'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sox_executable = 'sox'
        self.force = False
        self.subsample = False
        self.spectrogram = False
        self.species_lookup = SpeciesLookup()

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Name of the file or directory to import')
        parser.add_argument(
            '-r', '--recursive', action='store_true',
            help='Recurse in directory, finding all .wav files'
        )
        parser.add_argument(
            '-u', '--subsample', action='store_true', help='Generate subsampled audio files'
        )
        parser.add_argument(
            '-p', '--spectrogram', action='store_true', help='Generate spectrogram image files'
        )
        parser.add_argument(
            '-f', '--force', action='store_true', help='Process files even if already seen'
        )

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        recurse = kwargs['recursive']
        self.force = kwargs['force']
        self.subsample = kwargs['subsample']
        self.spectrogram = kwargs['spectrogram']

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

        existing_audio = AudioRecording.objects.filter(audio_file=filepath)
        result_count = len(existing_audio)
        if result_count:
            if result_count > 1:
                print(f'Got duplicate records ({result_count}) for {filepath}')
            audio = existing_audio[0]
            audio.identifier = filestem
            if audio.processed and not self.force:
                print("Already processed this file, skipping")
                return
            print('Found incomplete existing record, trying to update')
        else:
            audio = AudioRecording(audio_file=filepath, identifier=filestem)

        self.populate_audio_from_identifier(audio)

        try:
            # print(f'Looking for GUANO data for {filename}')
            guano_file = GuanoFile(filepath)
            if not guano_file:
                # print(f'Empty GUANO data for {filename}')
                guano_file = None
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
            try:
                self.populate_audio_from_wamd(audio, wamd_file)
            except ValueError:
                print("Could not load fallback WAMD data")

        if not audio.duration:
            self.read_file_duration(filename, audio)

        if self.subsample:
            self.subsample_file(audio)

        if self.spectrogram:
            self.generate_spectrogram_file(audio)

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
            if 'Timestamp' in guano_file and guano_file['Timestamp'] is not None:
                if guano_file['Timestamp'].utcoffset() is None:
                    print(
                        'Timestamp with no tzinfo from guano '
                        'cannot be saved'
                    )
                else:
                    audio.set_recording_time(guano_file['Timestamp'])
        except ValueError:
            print('Cannot use timestamp from guano - no valid TZ?')
        finally:
            audio.processed = True

    @staticmethod
    def populate_audio_from_identifier(audio):
        id_parser = TraceIdentifier(audio.identifier)
        if id_parser.matched:
            audio.set_recording_time(id_parser.datetime)
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

        audio.guano_data = json.dumps({'Source': 'WAMD data'})
        audio.processed = True

    def subsample_file(self, audio: AudioRecording):
        if not audio.id:
            audio.save()
        dest = os.path.join(
            settings.MEDIA_ROOT,
            'processed',
            'subsampled',
            f'{audio.id}-{audio.identifier}.wav'
        )
        print(f'Subsample {audio.audio_file} to {dest}')
        sox_result = subprocess.run([self.sox_executable, audio.audio_file, '-r44100', dest])
        sox_result.check_returncode()
        audio.subsampled_audio_file = dest

    def generate_spectrogram_file(self, audio: AudioRecording):
        prefilter = settings.SPECTROGRAM_PREFILTER
        credit = settings.SPECTROGRAM_CREDIT

        title = '(unknown) '

        if audio.species:
            title = f'{audio.genus} {audio.species} '
            try:
                species = self.species_lookup.species_by_abbreviations(audio.genus, audio.species)
            except NonUniqueSpeciesLookup:
                species = None

            if species:
                species_ucfirst = species.species[0].upper() + species.species[1:]
                if species.common_name:
                    title = f'{species.common_name} ({species.genus} {species_ucfirst}) '
                else:
                    title = f'{species.genus} {species_ucfirst} '

        if audio.recorded_at_iso:
            title += date_parser.parse(audio.recorded_at_iso).strftime('%Y-%m-%d %H:%M')

        if not audio.id:
            audio.save()
        dest = os.path.join(settings.MEDIA_ROOT, 'processed', 'spectrograms',
                            f'{audio.id}-{audio.identifier}.png')
        print(f'Plot {audio.audio_file} spectrum to {dest}')
        #     sox "$file" -n spectrogram -o "$outfile" -t "$ident"
        sox_result = subprocess.run(
            [self.sox_executable, audio.audio_file, '-n', ] +
            prefilter +
            ['spectrogram', '-o', dest, '-c', credit, '-t', title]
        )
        sox_result.check_returncode()
        png_reader = Reader(filename=dest)
        (width, height, _, _) = png_reader.read()
        audio.spectrogram_image_file = dest
        audio.spectrogram_image_width = width
        audio.spectrogram_image_height = height
