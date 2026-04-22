from http import HTTPStatus

from flask import request, jsonify

from yacut import app
from yacut.models import URLMap
from yacut.error_handlers import InvalidAPIUsage
from yacut.constants import (
    MAX_SHORT_LENGTH,
    NOT_FOUND,
    EMPTY_BODY,
    URL_REQUIRED,
    SHORT_INVALID,
)


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)

    if not data:
        raise InvalidAPIUsage(EMPTY_BODY)

    if 'url' not in data or not data['url']:
        raise InvalidAPIUsage(URL_REQUIRED)

    if 'custom_id' in data and data['custom_id']:
        if len(data['custom_id']) > MAX_SHORT_LENGTH:
            raise InvalidAPIUsage(SHORT_INVALID)

    try:
        url_map = URLMap.create(
            original=data['url'],
            short=data.get('custom_id')
        )
    except Exception as error:
        raise InvalidAPIUsage(str(error))

    return jsonify({
        'url': data['url'],
        'short_link': url_map.get_short_url()
    }), HTTPStatus.CREATED


@app.route('/api/id/<string:short>/', methods=['GET'])
def get_original_link(short):
    url_map = URLMap.get(short)

    if not url_map:
        return jsonify({
            'message': NOT_FOUND
        }), HTTPStatus.NOT_FOUND

    return jsonify({
        'url': url_map.original
    }), HTTPStatus.OK
