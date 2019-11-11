"""
Data lookup tools - find species names from DB
"""
from typing import List, Optional, Union

from .models import Species


class NonUniqueSpeciesLookup(Exception):
    """
    Exception subclass to be thrown if we try to fetch a non-unique record where unique is needed
    """

    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__(*args)
        self.alternatives = kwargs['alternatives']


class SpeciesLookup:
    """
    Tools to fetch species records
    """
    model = Species

    def __init__(self) -> None:
        super().__init__()
        self._species_lookup_cache = {}

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
        species_records = self.model.objects.filter(canon_genus_3code=abbreviation.upper()). \
            values('genus').distinct()
        if len(species_records) == 1:
            return species_records[0]['genus']

        # Otherwise, use heuristic lookup

        species_records = self.model.objects.filter(genus__istartswith=abbreviation). \
            values('genus').distinct()
        if len(species_records) == 1:
            return species_records[0]['genus']

        return [s['genus'] for s in species_records]

    def species_by_abbreviations(
            self,
            genus_abbreviation: str,
            species_abbreviation: str
    ) -> Optional[Species]:
        """
        Lookup a species by genus and species abbreviations
        Args:
            genus_abbreviation:
            species_abbreviation:

        Returns:

        """
        if len(genus_abbreviation) == 0 or len(species_abbreviation) == 0:
            return None

        composite_key = (genus_abbreviation + species_abbreviation).upper()
        if composite_key in self._species_lookup_cache:
            species_records = self._species_lookup_cache[composite_key]
        else:

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

            self._species_lookup_cache[composite_key] = list(species_records)

        if len(species_records) == 1:
            return species_records[0]

        if len(species_records) == 0:
            return None

        raise NonUniqueSpeciesLookup(alternatives=list(species_records))
