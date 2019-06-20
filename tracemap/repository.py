from .models import Species
from typing import List, Union, Optional


class NonUniqueSpeciesLookup(Exception):

    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__(*args)
        self.alternatives = kwargs['alternatives']


class SpeciesLookup:
    model = Species

    def genus_name_by_abbreviation(self, abbreviation: str) -> Union[None, str, List[str]]:
        """
        Return a list of candidate genus for a given prefix

        Args:
            abbreviation: first few letters

        Returns:
            A single Species, if available
        """
        if len(abbreviation) == 0:
            return None

        # First see if we've got it fixed:
        species_records = self.model.objects.filter(canon_genus_3code=abbreviation.upper()).values('genus').distinct()
        if len(species_records) == 1:
            return species_records[0]['genus']

        # Otherwise, use heuristic lookup

        species_records = self.model.objects.filter(genus__istartswith=abbreviation).values('genus').distinct()
        if len(species_records) == 1:
            return species_records[0]['genus']
        else:
            return [s['genus'] for s in species_records]

    def species_by_abbreviations(self, genus_abbreviation: str, species_abbreviation: str) -> Optional[Species]:
        if len(genus_abbreviation) == 0 or len(species_abbreviation) == 0:
            return None

        # First try a canon lookup:
        species_records = self.model.objects.filter(
            canon_genus_3code=genus_abbreviation.upper(),
            species__istartswith=species_abbreviation,
        )

        if len(species_records) == 0:  # Else go heuristic
            species_records = self.model.objects.filter(
                genus__istartswith=genus_abbreviation,
                species__istartswith=species_abbreviation,
            )

        if len(species_records) == 1:
            return species_records[0]
        elif len(species_records) == 0:
            return None
        else:
            raise NonUniqueSpeciesLookup(alternatives=list(species_records))
