import logging
import time
from typing import TYPE_CHECKING

import yandex_music

from ytm_to_yam.model.album import Album
from ytm_to_yam.model.track import Track
from ytm_to_yam.util import retry

if TYPE_CHECKING:
    from yandex_music import Track as YAMTrack
    from yandex_music import Playlist as YAMPlaylist
    from ytm_to_yam.model.artist import Artist
    from ytm_to_yam.model.playlist import Playlist

logger = logging.getLogger(__name__)


class YAM:
    def __init__(self, token: str):
        if not token:
            raise ValueError('YAM token is required')
        self.client = yandex_music.Client(token=token).init()

    @retry
    def like_artist(self, artist: 'Artist'):
        search_result = self.client.search(artist.name, type_='artist')
        if (search_result is None or search_result.artists is None
                or search_result.artists.total == 0):
            logger.warning('Skipped artist "%s": not found', artist.name)
            return

        found_artist = search_result.artists.results[0]

        if found_artist.name.lower() != artist.name.lower():
            logger.warning('Skipped artist "%s": best found match is "%s"',
                           artist.name,
                           found_artist.name)
            return

        success = found_artist.like()
        if success:
            logger.info('Liked artist "%s"', artist.name)
        else:
            logger.error('Failed to like artist "%s"', artist.name)

        self._sleep_after_api_call()

    @retry
    def like_album(self, album: 'Album'):
        search_result = self.client.search(album.search_query, type_='album')
        if (search_result is None or search_result.albums is None
                or search_result.albums.total == 0):
            logger.warning('Skipped album "%s": not found', album.full_name)
            return

        found_album = search_result.albums.results[0]

        found_title = found_album.title
        found_year = found_album.year
        found_full_name = Album.generate_full_name(found_album.artists, found_title, found_year)
        found_first_artist_name = found_album.artists[0].name
        first_artist_name = album.artists[0].name

        # here we do not check year to avoid any inconsistency between two services
        if found_title.lower() != album.title.lower() \
                or found_first_artist_name.lower() != first_artist_name.lower():
            logger.warning('Skipped album "%s": best found match is "%s"',
                           album.full_name,
                           found_full_name)
            return

        success = found_album.like()
        if success:
            logger.info('Liked album "%s"', album.full_name)
        else:
            logger.error('Failed to like album "%s"', album.full_name)

        self._sleep_after_api_call()

    @retry
    def sync_playlist(self, playlist: 'Playlist'):
        yam_playlists = self.client.users_playlists_list()

        for yam_playlist in yam_playlists:
            if yam_playlist.title == playlist.title:
                logger.info('Going to sync playlist "%s"', playlist.title)
                self._sync_playlist(yam_playlist, playlist)
                return

        yam_playlist = self.client.users_playlists_create(title=playlist.title,
                                                          visibility='private')
        logger.info('Going to sync new playlist "%s"', playlist.title)
        self._sync_playlist(yam_playlist, playlist)

    def _sync_playlist(self, yam_playlist: 'YAMPlaylist', playlist: 'Playlist'):
        for track in playlist.tracks:

            if not track.artists:
                logger.warning('%s. Skipped track "%s": unknown artists', playlist.title, track.full_name)
                continue

            if self.has_yam_playlist_track(yam_playlist, track):
                logger.debug('%s. Skipped track "%s": already in playlist', playlist.title, track.full_name)
                continue

            search_result = self.client.search(track.search_query, type_='track')

            if (search_result is None or search_result.tracks is None
                    or search_result.tracks.total == 0):
                logger.warning('%s. Skipped track "%s": not found', playlist.title, track.full_name)
                continue

            found_track = search_result.tracks.results[0]
            if not found_track.artists:
                logger.warning('%s. Skipped track "%s": no artist found', playlist.title, track.full_name)
                continue

            if not self.are_tracks_match(track, found_track):
                full_name = Track.generate_full_name(found_track.artists, found_track.albums[0], found_track.title)

                logger.warning('%s. Skipped track "%s": best found match is "%s"',
                               playlist.title,
                               track.full_name,
                               full_name
                               )
                continue

            if ':' in found_track.track_id:
                track_id, album_id = list(map(int, found_track.track_id.split(':')))
            else:
                track_id, album_id = found_track.id, None

            yam_playlist = yam_playlist.insert_track(track_id, album_id)
            logger.info('%s. Inserted track %s', playlist.title, track.full_name)
            self._sleep_after_api_call()

    @staticmethod
    def are_tracks_match(track: 'Track', yam_track: 'YAMTrack') -> bool:
        yam_artist = yam_track.artists[0]
        artist = track.artists[0]

        return yam_track.title.lower() == track.title.lower() \
            and yam_artist.name.lower() == artist.name.lower()

    @staticmethod
    def has_yam_playlist_track(yam_playlist: 'YAMPlaylist', track: 'Track') -> bool:
        track_artist_name = track.artists[0].name if track.artists else ''
        track_title = track.title

        for yam_track in yam_playlist.fetch_tracks():

            yam_track_title = yam_track.track.title
            yam_artist_name = yam_track.track.artists[0].name if yam_track.track.artists else ''
            if track_title.lower() == yam_track_title.lower() \
                    and track_artist_name.lower() == yam_artist_name.lower():
                return True

        return False

    @staticmethod
    def _sleep_after_api_call():
        time.sleep(0.1)
