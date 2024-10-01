from typing import List, Union, Optional

from ytm_to_yam.model.artist import Artist
from yandex_music import Artist as YAMArtist


class Album:
    def __init__(self, artists: List['Artist'], title: str, year: Optional[Union[str, int]]):
        self.artists = artists
        self.title = title
        self.year = int(year) if year else None

    @property
    def search_query(self) -> str:
        return f'{self.artists[0].name} {self.title}'

    @property
    def full_name(self) -> str:
        return self.generate_full_name(self.artists, self.title, self.year)


    @staticmethod
    def generate_full_name(artists: List[Union['Artist', 'YAMArtist', str]], title: str, year: Union[str, int]) -> str:
        artist_names = ','.join(
            a.name if isinstance(a, (Artist, YAMArtist)) else a
            for a in artists
        )
        return f'{artist_names} - {year} - {title}'

    def __repr__(self):
        return f"Album({repr(self.artists)}, {repr(self.title)}, {repr(self.year)})"
