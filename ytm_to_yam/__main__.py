import argparse
import logging
import os
import sys


from ytm_to_yam.yam import YAM
from ytm_to_yam.ytm import YTM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sync_ytm_to_yam')


def main():
    args = parse_args()
    ytm = YTM(args.ytm_auth_file)
    yam = YAM(args.yam_token)

    # sync_artists(ytm, yam)
    # sync_albums(ytm, yam)
    sync_playlists(ytm, yam)

def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('--yam-token', default=os.environ.get('YAM_TOKEN'), dest='yam_token',
                        help='Yandex Music token. If not specified, then used value of YAM_TOKEN environment variable.')
    parser.add_argument('--ytm-auth-file', default='browser.json', dest='ytm_auth_file',
                        help='Youtube Music JSON file with auth data. Defaults to browser.json in current working directory.')

    return parser.parse_args(args)


def sync_artists(ytm: 'YTM', yam: 'YAM'):
    logger.info('Going to sync ARTISTS')
    artists = ytm.get_artists()

    logger.info('%d artists subscriptions in YTMusic', len(artists))
    for artist in artists:
        yam.like_artist(artist)


def sync_albums(ytm: 'YTM', yam: 'YAM'):
    logger.info('Going to sync ALBUMS')
    albums = ytm.get_albums()

    logger.info('%d albums subscriptions in YTMusic', len(albums))
    for album in albums:
        yam.like_album(album)


def sync_playlists(ytm: 'YTM', yam: 'YAM'):
    logger.info('Going to sync PLAYLISTS')
    playlists = ytm.get_playlists()

    logger.info('%d playlists in YTMusic', len(playlists))
    for playlist in playlists:
        yam.sync_playlist(playlist)


if __name__ == '__main__':
    main()
