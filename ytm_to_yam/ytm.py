import functools
import time
from typing import List

import requests
import ytmusicapi

from ytm_to_yam.model.album import Album
from ytm_to_yam.model.artist import Artist
from ytm_to_yam.model.playlist import Playlist
from ytm_to_yam.util import retry


class YTM:
    def __init__(self, ytm_auth_file):
        session = requests.Session()
        session.request = functools.partial(session.request, timeout=120)
        self.client = ytmusicapi.YTMusic(auth=ytm_auth_file,
                                         requests_session=session)

    @retry
    def get_artists(self) -> List[Artist]:
        ytm_artists = self.client.get_library_subscriptions(limit=None)
        return [Artist(name=artist['artist']) for artist in ytm_artists]

    @retry
    def get_albums(self) -> List[Album]:
        ytm_albums = self.client.get_library_albums(limit=None)
        albums = []
        for ytm_album in ytm_albums:
            artists = [Artist(name=a['name']) for a in ytm_album['artists']]
            album = Album(artists=artists, title=ytm_album['title'], year=ytm_album['year'])
            albums.append(album)
        return albums

    @retry
    def get_playlists(self) -> List[Playlist]:
        ytm_playlists_meta = self.client.get_library_playlists(limit=None)
        playlists = []
        for ytm_playlist_meta in ytm_playlists_meta:
            ytm_playlist = self.client.get_playlist(ytm_playlist_meta['playlistId'])

            playlists.append(Playlist.from_ytm_playlist(ytm_playlist))

        return playlists

    @staticmethod
    def _sleep_after_api_call():
        time.sleep(0.2)