from typing import TYPE_CHECKING, List, Optional, Union

from yandex_music import Artist as YAMArtist
from ytm_to_yam.model.artist import Artist

if TYPE_CHECKING:
    from yandex_music import Album as YAMAlbum
    from ytm_to_yam.model.album import Album


class Track:
    def __init__(self, artists: Optional[List['Artist']], album: Optional['Album'], title: str):
        self.artists = artists
        self.album = album
        self.title = title

    @property
    def search_query(self) -> str:
        if self.artists:
            return f'{self.artists[0].name} {self.title}'
        else:
            return self.title

    @property
    def full_name(self) -> str:
        return self.generate_full_name(self.artists, self.album, self.title)

    @staticmethod
    def generate_full_name(artists: List[Union['Artist', 'YAMArtist', str]], album: Union['Album', 'YAMAlbum'],
                           title: str) -> str:
        if not artists:
            artists_part = 'UNKNOWN ARTISTS'
        else:
            artists_part = ','.join(
                a.name if isinstance(a, (Artist, YAMArtist)) else a
                for a in artists
            )

        if not album:
            album_part = 'UNKNOWN ALBUM'
        else:
            album_part = f'({album.title}'
        return f'{artists_part} - {album_part} - {title}'

    def __repr__(self):
        return f"Track({repr(self.artists)}, {repr(self.album)}, {repr(self.title)})"
