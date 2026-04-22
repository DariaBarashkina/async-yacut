from http import HTTPStatus

from flask import jsonify, render_template, request

from yacut import app, db
from yacut.constants import INTERNAL_ERROR, RESOURCE_NOT_FOUND


class InvalidAPIUsage(Exception):
    """Кастомное исключение для ошибок API."""

    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__()
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        return {'message': self.message}


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    if request.path.startswith('/api/'):
        return jsonify(
            {'message': RESOURCE_NOT_FOUND}
        ), HTTPStatus.NOT_FOUND
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify(
            {'message': INTERNAL_ERROR}
        ), HTTPStatus.INTERNAL_SERVER_ERROR
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR
