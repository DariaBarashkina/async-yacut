import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URI',
        'sqlite:///db.sqlite3'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DISK_TOKEN = os.environ.get('DISK_TOKEN')

    YANDEX_API_BASE = 'https://cloud-api.yandex.net/v1'
