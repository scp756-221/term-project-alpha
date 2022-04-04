"""
These tests are invoked by running `pytest` with the
appropriate options and environment variables, as
defined in `conftest.py`.
"""

# Standard libraries

# Installed packages
import pytest

# Local modules
# for creating music records before adding to the playlist
import music
import playlist


@pytest.fixture
def playlist_serv(request, playlist_url, auth):
    return playlist.Playlist(playlist_url, auth)


@pytest.fixture
def mserv(request, music_url, auth):
    return music.Music(music_url, auth)


@pytest.fixture
def song(request):
    # Recorded 1956
    return ('Elvis Presley', 'Hound Dog')


def test_playlist_create(playlist_serv, mserv, song):
    trc, music_id = mserv.create(song[0], song[1])
    music_ids = []
    music_ids.append(music_id)
    playlist_name = "Mock playlist"
    trc, created_playlist_detail = playlist_serv.create_playlist(playlist_name,
                                                                 music_ids)
    playlist_id = created_playlist_detail['playlist_id']
    print(playlist_id)
    assert (trc == 200)
    trc, pl_details = playlist_serv.get_playlist_details(playlist_id)
    print(pl_details)
    assert (trc == 200)
    playlist_serv.delete_playlist(playlist_id)
    mserv.delete(music_id)


# @pytest.fixture
# def song_oa(request):
#     # Recorded 1967
# return ('Aretha Franklin', 'Respect')


# @pytest.fixture
# def m_id_oa():
    # assert (200 == 200)
