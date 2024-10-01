from typing import List

from ytm_to_yam.model.album import Album
from ytm_to_yam.model.artist import Artist
from ytm_to_yam.model.track import Track


class Playlist:
    def __init__(self, title: str, tracks: List['Track']):
        self.title = title
        self.tracks = tracks

    @staticmethod
    def from_ytm_playlist(ytm_playlist) -> 'Playlist':
        tracks = []
        playlist_title = f'{ytm_playlist['title']} (YTM)'

        for ytm_track in ytm_playlist['tracks']:
            artists = []
            album = None
            track_title = ytm_track['title']

            ytm_album = ytm_track['album']
            ytm_artists = ytm_track['artists'] or []

            for ytm_artist in ytm_artists:
                artists.append(Artist(name=ytm_artist['name']))

            if ytm_album:
                album = Album(artists, ytm_album['name'], year=None)

            track = Track(artists, album, track_title)

            tracks.append(track)

        return Playlist(playlist_title, tracks)
