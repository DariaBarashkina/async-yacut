import re
from http import HTTPStatus

from flask import request, jsonify

from yacut import app
from yacut.models import URLMap
from yacut.error_handlers import InvalidAPIUsage
from yacut.constants import MAX_SHORT_LENGTH, ALLOWED_CHARS, NOT_FOUND


ERROR_NO_BODY = 'Отсутствует тело запроса'
ERROR_NO_URL = '"url" является обязательным полем!'
ERROR_INVALID_SHORT = 'Указано недопустимое имя для короткой ссылки'


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json(silent=True)

    if not data:
        raise InvalidAPIUsage(ERROR_NO_BODY)

    if 'url' not in data or not data['url']:
        raise InvalidAPIUsage(ERROR_NO_URL)

    custom_id = data.get('custom_id')

    if custom_id:
        if len(custom_id) > MAX_SHORT_LENGTH:
            raise InvalidAPIUsage(ERROR_INVALID_SHORT)

        if not re.fullmatch(rf'^[{ALLOWED_CHARS}]+$', custom_id):
            raise InvalidAPIUsage(ERROR_INVALID_SHORT)

    try:
        obj = URLMap.create(
            original=data['url'],
            short=custom_id
        )
    except ValueError as e:
        raise InvalidAPIUsage(str(e))

    return jsonify({
        'url': obj.original,
        'short_link': obj.get_short_url()
    }), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_original_link(short_id):
    url_map = URLMap.get(short_id)

    if not url_map:
        return jsonify({
            'message': NOT_FOUND
        }), HTTPStatus.NOT_FOUND

    return jsonify({
        'url': url_map.original
    }), HTTPStatus.OK
