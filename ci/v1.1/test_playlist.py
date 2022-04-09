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


@pytest.fixture
def song_to_add(request):
    # Recorded 1956
    return ('Linkin Park', 'In the end')


def test_playlist_create(playlist_serv, mserv, song):
    trc, music_id = mserv.create(song[0], song[1])
    music_ids = []
    music_ids.append(music_id)
    playlist_name = "Mock playlist"
    trc, created_playlist_detail = playlist_serv.create_playlist(playlist_name,
                                                                 music_ids)
    playlist_id = created_playlist_detail['playlist_id']
    assert (trc == 200)
    trc, pl_details = playlist_serv.get_playlist_details(playlist_id)
    pl_details_items = pl_details['Items'][0]
    # playlist_id = created_playlist_detail['playlist_id']
    plalist_name_from_db = pl_details_items['Playlist_Name']
    playlist_songs = pl_details_items['Music_IDs']
    assert (trc == 200 and plalist_name_from_db == playlist_name
            and music_id in playlist_songs)
    playlist_serv.delete_playlist(playlist_id)
    mserv.delete(music_id)


def test_add_song_to_playlist(playlist_serv, mserv, song, song_to_add):
    trc, song_id = mserv.create(song[0], song[1])
    song_ids = []
    song_ids.append(song_id)
    playlist_name = "Mock playlist"
    trc, created_playlist_detail = playlist_serv.create_playlist(playlist_name,
                                                                 song_ids)
    playlist_id = created_playlist_detail['playlist_id']
    song_ids_to_add = []
    trc, new_song_id = mserv.create(song_to_add[0], song_to_add[1])
    song_ids_to_add.append(new_song_id)
    trc, updated_details = playlist_serv.add_song_to_playlist(playlist_id,
                                                              song_ids_to_add)
    update_message_expected = 'Music added successfully'
    update_message_actual = updated_details['Message']
    updated_playlist = updated_details['Updated Playlist']
    updated_playlist_name_actual = updated_playlist['Playlist_Name']
    updated_playlist_songs_actual = updated_playlist['Music_IDs']
    assert (trc == 200 and update_message_expected == update_message_actual
            and playlist_name == updated_playlist_name_actual
            and len(updated_playlist_songs_actual) == 2
            and song_id in updated_playlist_songs_actual
            and new_song_id in updated_playlist_songs_actual)
    playlist_serv.delete_playlist(playlist_id)
    mserv.delete(song_id)
    mserv.delete(new_song_id)


def test_remove_song_to_playlist(playlist_serv, mserv, song):
    trc, song_id = mserv.create(song[0], song[1])
    song_ids = []
    song_ids.append(song_id)
    playlist_name = "Mock playlist"
    trc, created_playlist_detail = playlist_serv.create_playlist(playlist_name,
                                                                 song_ids)
    playlist_id = created_playlist_detail['playlist_id']
    trc, updated_details = playlist_serv.remove_song_from_playlist(playlist_id,
                                                                   song_ids
                                                                   )
    update_message_expected = 'Music removed successfully'
    update_message_actual = updated_details['Message']
    updated_playlist = updated_details['Updated Playlist']
    updated_playlist_name_actual = updated_playlist['Playlist_Name']
    updated_playlist_songs_actual = updated_playlist['Music_IDs']
    assert (trc == 200 and update_message_expected == update_message_actual
            and playlist_name == updated_playlist_name_actual
            and len(updated_playlist_songs_actual) == 0
            and song_id not in updated_playlist_songs_actual)
    playlist_serv.delete_playlist(playlist_id)
    mserv.delete(song_id)


def test_remove_song_to_playlist_for_error(playlist_serv, mserv, song):
    trc, song_id = mserv.create(song[0], song[1])
    song_ids = []
    song_ids.append(song_id)
    playlist_name = "Mock playlist"
    trc, created_playlist_detail = playlist_serv.create_playlist(playlist_name,
                                                                 song_ids)
    playlist_id = created_playlist_detail['playlist_id']
    trc, updated_details = playlist_serv.remove_song_from_playlist_error(
                                                                   playlist_id,
                                                                   song_ids
                                                                   )
    update_message_expected = 'Music removed successfully'
    update_message_actual = updated_details['Message']
    assert (trc == 400 and update_message_expected != update_message_actual)
    playlist_serv.delete_playlist(playlist_id)
    mserv.delete(song_id)
