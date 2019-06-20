from django.core.management.base import BaseCommand
import csv
from tracemap.models import Species


class Command(BaseCommand):
    help = 'Load CSV file from https://mammaldiversity.org into database'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Name of the file or directory to import')

    def handle(self, *args, **kwargs):
        required_csv_fields = ['genus', 'species', 'common name', 'linnean order']
        filename = kwargs['filename']
        column_map = {}
        i = 0
        with open(filename, newline='', encoding='ISO-8859–1') as csvfile:  # Export is currently not utf8
            reader = csv.reader(csvfile)

            row = next(reader)
            # print(row)
            for index in range(0, len(row)):
                column_map[row[index].lower()] = index

            print(column_map)
            for field in required_csv_fields:
                if field not in column_map.keys():
                    print(f"Can't find all required headers in CSV: {', '.join(required_csv_fields)}")
                    exit(1)

            o = column_map['linnean order']
            g = column_map['genus']
            s = column_map['species']
            c = column_map['common name']

            new = 0

            for row in reader:
                i += 1
                if len(row) > o and row[o].lower() == 'chiroptera':  # non-blank
                    genus = row[g]
                    species = row[s]
                    common_name = row[c]
                    existing_species = Species.objects.filter(genus=genus, species=species)
                    hits = len(existing_species)
                    if hits == 0:
                        species_record = Species()
                        species_record.species = species
                        species_record.genus = genus
                        species_record.common_name = common_name
                        species_record.save()
                        print(f'Added {genus} {species} ({common_name})')
                        new += 1
                    elif hits == 1:
                        species_record = existing_species[0]
                        print(f'Found {genus} {species}, skipping')
                    else:
                        print(f'Already have multiple hits for {genus} {species}')

        print(f'Read {i} rows, found {new} new bats')
