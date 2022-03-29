# Standard library modules
import logging
import os
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
    "create_playlist" : "Playlist Created"
}

error_messages = {
    "create_payload_error" : "Request body is not correct. Keys needed: Playlist Name, Song IDs."
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
    headers = request.headers
    return "API is working. Please access the required URL"


def get_song_details(music_id, headers):
    payload = {"objtype": "music", "objkey": music_id}
    url = db['name'] + '/' + db['endpoint'][0]
    response = requests.get(
        url,
        params=payload,
        headers={'Authorization': headers['Authorization']})
    return (response.json())


@bp.route('/<playlist_id>', methods=['GET'])
def get_playlist_details(playlist_id):
    pass

@bp.route('/', methods=['POST'])
def create_playlist():
    headers = request.headers
    # check header here
    # if 'Authorization' not in headers:
    #     return Response(json.dumps({"error": "missing auth"}),
    #                     status=401,
    #                     mimetype='application/json')
    try:
        content = request.get_json()
        playlist_name = content['Playlist Name']
        songs = content['Song IDs']
    except Exception:
        return Response(json.dumps({"Message": error_messages['create_payload_error']}),
                        status=400, mimetype='application/json')

    #check the songs are exitisng in the DB 
    for song in songs:
        music_api_reponse = get_song_details(song, headers)
        # make sure there is an existing record for the music/song
        # to be added
        if music_api_reponse['Count'] == 1:
            continue
        else:
            return Response(json.dumps({"Message": error_messages['missing_song_record_error'].format(song)}),
                        status=400, mimetype='application/json')
    #save to DB
    url = db['name'] + '/' + db['endpoint'][1]
    request_body = {"objtype": "playlist", 
                    "Playlist Name": playlist_name, 
                    "Songs": songs}
    response = requests.post(url, json=request_body, headers={'Authorization': headers['Authorization']})
    return Response(json.dumps({"Message" : success_messages['create_playlist'], "Playlist Details": response.json()}), 
                    status=200, mimetype='application/json')

@bp.route('/add/', methods=['POST'])
def add_song_to_playlist():
    pass
        

@bp.route('/remove/', methods=['POST'])
def remove_song_from_playlist():
    pass

@bp.route('/<playlist_id>', methods=['DELETE'])
def delete_playlist(playlist_id):
    pass


# All database calls will have this prefix.  Prometheus metric
# calls will not---they will have route '/metrics'.  This is
# the conventional organization.

app.register_blueprint(bp, url_prefix='/api/v1/playlists/')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        logging.error("missing port arg 1")
        sys.exit(-1)
    p = int(sys.argv[1])
    # Do not set debug=True---that will disable the Prometheus metrics
    app.run(host='0.0.0.0', port=p, threaded=True)

