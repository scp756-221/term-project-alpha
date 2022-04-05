# Standard library modules
import logging
import sys

# Installed packages
from flask import Blueprint
from flask import Flask
from flask import request
from flask import Response

from prometheus_flask_exporter import PrometheusMetrics

import requests

import simplejson as json

app = Flask(__name__)

metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Playlist process')

db = {
    "name": "http://cmpt756db:30002/api/v1/datastore",
    "endpoint": [
        "read",
        "write",
        "delete",
        "update"
    ]
}

success_messages = {
    "create_playlist": "Playlist Created",
    "add_song": "Song added successfully",
    "remove_song": "Song removed successfully",
    "delete_playlist": "Playlist Deleted"
}

error_messages = {
    "create_payload_error": "Request body is not correct."
                            " Keys needed: Playlist Name, Song IDs.",
    "add_song_payload_error": "Request body is not correct."
                              " Keys needed: Playlist ID, Songs IDs To Add.",
    "remove_song_payload_error": "Request body is not"
                                 " correct. Keys needed: Playlist ID,"
                                 " Songs IDs To Remove.",
    "no_or_multiple_playlist_records_error": "No / Multiple records found for "
                                             "the Playlist ID."
                                             " Please verify it is correct.",
    "general_processing_error": "Exception occurred while"
                                " processing your request."
                                " Please reach out to the developers.",
    "db_save_error": "Exception occured while saving the data to the database."
                     " Please reach out to the developers.",
    "db_delete_error": "Exception while deleting the playlist."
                       " Please reach out to the developers.",
    "missing_song_record_error": "No record found in Music"
                                 " table for the song ID: {}",
    "song_not_in_playlist_error": "Playlist does not have the song ID: {}."
                                  " Unable to process the request"
}

bp = Blueprint('app', __name__)


@bp.route('/health')
@metrics.do_not_track()
def health():
    return Response("", status=200, mimetype="application/json")


@bp.route('/readiness')
@metrics.do_not_track()
def readiness():
    return Response("", status=200, mimetype="application/json")


@bp.route('/', methods=['GET'])
@metrics.do_not_track()
def list_all():
    return "API is working. Please access the required URL"


def get_song_details(music_id, headers):
    payload = {"objtype": "music", "objkey": music_id}
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(
        url,
        params=payload,
        headers={'Authorization': headers['Authorization']})
    return response.json()


@bp.route('/<playlist_id>', methods=['GET'])
def get_playlist_details(playlist_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    payload = {"objtype": "playlist", "objkey": playlist_id}
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(
        url,
        params=payload,
        headers={'Authorization': headers['Authorization']})
    response_json = response.json()
    # TODO
    # add handling if response isn't found
    return response_json


@bp.route('/', methods=['POST'])
def create_playlist():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        playlist_name = content['Playlist Name']
        songs = content['Song IDs']
    except Exception:
        return Response(json.dumps(
            {"Message": error_messages['create_payload_error']}),
            status=400, mimetype='application/json')

    # check the songs are existing in the DB
    for song in songs:
        music_api_response = get_song_details(song, headers)
        # make sure there is an existing record for the music/song
        # to be added
        if music_api_response['Count'] == 1:
            continue
        else:
            return Response(json.dumps(
                {"Message": error_messages['missing_song_record_error'].
                    format(song)}),
                status=400, mimetype='application/json')
    # save to DB
    url = db['name'] + '/' + db['endpoint'][1]
    request_body = {"objtype": "playlist",
                    "Playlist Name": playlist_name,
                    "Songs": songs}
    response = requests.post(url,
                             json=request_body,
                             headers={
                                 'Authorization': headers['Authorization']}
                             )
    return Response(json.dumps({"Message": success_messages['create_playlist'],
                                "Playlist Details": response.json()}),
                    status=200, mimetype='application/json')


@bp.route('/add/', methods=['PUT'])
def add_song_to_playlist():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        playlist_id = content['Playlist ID']
        new_songs_to_add = content['Songs IDs To Add']
    except Exception:
        return Response(json.dumps({
            "Message": error_messages['add_song_payload_error']}),
            status=400, mimetype='application/json')

    # get existing details of the playlist
    response_items = {}
    try:
        playlist_details = get_playlist_details(playlist_id)
        if playlist_details['Count'] != 1:
            return Response(json.dumps({
                "Message":
                    error_messages['no_or_multiple_playlist_records_error']}),
                status=400, mimetype='application/json')
        else:
            response_items = playlist_details['Items']
            for song in new_songs_to_add:
                music_api_response = get_song_details(song, headers)
                # make sure there is an existing record for the music/song
                # to be added
                if music_api_response['Count'] == 1:
                    continue
                else:
                    return Response(json.dumps({
                        "Message":
                        error_messages['missing_song_record'].format(song)}),
                        status=400, mimetype='application/json')
            response_items[0]['Songs'].extend(new_songs_to_add)
    except Exception:
        return Response(json.dumps({
            "Message": error_messages['general_processing_error']}),
            status=500, mimetype='application/json')
    # save to DB
    url = db['name'] + '/' + db['endpoint'][3]
    request_body = {"objtype": "playlist",
                    "objkey": playlist_id,
                    }
    try:
        _ = requests.put(
            url,
            params=request_body,
            json={
                "Songs": list(set(response_items[0]['Songs']))
            },
            headers={
                'Authorization': headers['Authorization']
            })
        updated_playlist_details = \
            get_playlist_details(playlist_id)['Items'][0]
        return Response(json.dumps({
            "Message": success_messages['add_song'],
            "Updated Playlist": updated_playlist_details}),
            status=200, mimetype='application/json')
    except Exception:
        return Response(json.dumps({
            "Message": error_messages['db_save_error']}),
            status=500, mimetype='application/json')


@bp.route('/remove/', methods=['PUT'])
def remove_song_from_playlist():
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    try:
        content = request.get_json()
        playlist_id = content['Playlist ID']
        songs_to_remove = content['Songs IDs To Remove']
    except Exception:
        return Response(json.dumps({
            "Message": error_messages['remove_song_payload_error']
        }),
            status=400, mimetype='application/json')

    # get existing details of the playlist
    response_items = {}
    try:
        playlist_details = get_playlist_details(playlist_id)
        if playlist_details['Count'] != 1:
            return Response(json.dumps({
                "Message":
                    error_messages['no_or_multiple_playlist_records_error']}),
                status=400, mimetype='application/json')
        else:
            response_items = playlist_details['Items']
            for song in songs_to_remove:
                if song in response_items[0]['Songs']:
                    response_items[0]['Songs'].remove(song)
                else:
                    return Response(json.dumps({
                        "Message":
                            error_messages
                            ['song_not_in_playlist_error'].format(song)}),
                        status=400, mimetype='application/json')
    except Exception:
        return Response(json.dumps({
            "Message": error_messages['general_processing_error']}),
            status=500, mimetype='application/json')
    # save to DB
    url = db['name'] + '/' + db['endpoint'][3]
    request_body = {"objtype": "playlist", "objkey": playlist_id}
    try:
        _ = requests.put(url, params=request_body, json={
            "Songs": response_items[0]['Songs']},
                         headers={'Authorization': headers['Authorization']})
        updated_playlist_details = \
            get_playlist_details(playlist_id)['Items'][0]
        return Response(
            json.dumps({
                "Message": success_messages['remove_song'],
                "Updated Playlist": updated_playlist_details}),
            status=200, mimetype='application/json')
    except Exception:
        return Response(json.dumps({
            "Message": error_messages['db_save_error']}),
            status=500, mimetype='application/json')


@bp.route('/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    headers = request.headers
    # check header here
    if 'Authorization' not in headers:
        return Response(json.dumps({"error": "missing auth"}),
                        status=401,
                        mimetype='application/json')
    url = db['name'] + '/' + db['endpoint'][2]
    try:
        _ = requests.delete(url, params={
            "objtype": "playlist", "objkey": playlist_id},
            headers={'Authorization': headers['Authorization']})
        return Response(json.dumps({
            "Message": success_messages['delete_playlist']}),
            status=200, mimetype='application/json')
    except Exception:
        return Response(json.dumps({
            "Message": error_messages['db_delete_error']}),
            status=500, mimetype='application/json')


# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.
# Trigger Build Yes


app.register_blueprint(bp, url_prefix='/api/v1/playlists/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("missing port arg 1")
        sys.exit(-1)
    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)
