import os

from yacut.constants import (
    ALLOWED_CHARS,
    MAX_SHORT_LENGTH,
    MAX_URL_LENGTH,
    SHORT_LENGTH,
)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI',
        'sqlite:///db.sqlite3'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DISK_TOKEN = os.environ.get('DISK_TOKEN')
    SHORT_LENGTH = SHORT_LENGTH
    MAX_SHORT_LENGTH = MAX_SHORT_LENGTH
    MAX_URL_LENGTH = MAX_URL_LENGTH
    ALLOWED_CHARS = ALLOWED_CHARS
