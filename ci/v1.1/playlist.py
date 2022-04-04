"""
Python  API for the music service.
"""

# Standard library modules

# Installed packages
import requests


class Playlist():
    """Python API for the music service.

    Handles the details of formatting HTTP requests and decoding
    the results.

    Parameters
    ----------
    url: string
        The URL for accessing the music service. Often
        'http://cmpt756s2:30001/'. Note the trailing slash.
    auth: string
        Authorization code to pass to the music service. For many
        implementations, the code is required but its content is
        ignored.
    """
    def __init__(self, url, auth):
        self._url = url
        self._auth = auth

    def create_playlist(self, playlist_name, songIds):
        payload = {'Playlist Name': playlist_name,
                   'Song IDs': songIds}
        r = requests.post(
            self._url,
            json=payload,
            headers={'Authorization': self._auth}
        )
        return r.status_code, r.json()['Playlist Details']

    def get_playlist_details(self, playlist_id):
        r = requests.get(
            self._url + playlist_id,
            headers={'Authorization': self._auth}
        )
        print(r.json())
        return r.status_code, r.json()

    def delete_playlist(self, playlist_id):
        requests.delete(
            self._url + playlist_id,
            headers={'Authorization': self._auth}
        )

    def add_song_to_playlist(self, playlist_id, songs_to_add):
        payload = {'Playlist ID': playlist_id,
                   'Songs IDs To Add': songs_to_add}
        r = requests.post(
            self._url + 'add/',
            json=payload,
            headers={'Authorization': self._auth}
        )
        return r.status_code, r.json()

    def remove_song_from_playlist(self, playlist_id, songs_to_remove):
        payload = {'Playlist ID': playlist_id,
                   'Songs IDs To Remove': songs_to_remove}
        r = requests.post(
            self._url + 'remove/',
            json=payload,
            headers={'Authorization': self._auth}
        )
        return r.status_code, r.json()

    def remove_song_from_playlist_error(self, playlist_id, songs_to_remove):
        """
        the remove end point requires the JSON payload to have
        a key 'Songs IDs To Remove' which will not be sent and
        the api should result in an error with HTTP 400 error
        """
        payload = {'Playlist ID': playlist_id}
        r = requests.post(
            self._url + 'remove/',
            json=payload,
            headers={'Authorization': self._auth}
        )
        return r.status_code, r.json()
