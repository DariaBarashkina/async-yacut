import random
import re
from datetime import datetime

from flask import url_for

from yacut import db
from yacut.constants import (
    SHORT_ALLOWED_CHARS,
    MAX_GENERATION_ATTEMPTS,
    RESERVED_SHORTS,
    SHORT_LENGTH,
    MAX_URL_LENGTH,
    MAX_SHORT_LENGTH,
    SHORT_EXISTS,
    SHORT_INVALID,
    REDIRECT_FOR_SHORT,
    SHORT_REGEX_PATTERN,
)


GENERATE_ERROR = 'Не удалось сгенерировать уникальный short'


class URLMap(db.Model):
    """Модель соответствия оригинальной и короткой ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_URL_LENGTH), nullable=False)
    short = db.Column(
        db.String(MAX_SHORT_LENGTH),
        unique=True,
        nullable=False,
        index=True
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def get(short):
        """Возвращает запись по короткому идентификатору."""
        return URLMap.query.filter_by(short=short).first()

    @staticmethod
    def create(original, short=None, commit=True, validate=True):
        """
        Создаёт запись в базе.
        """

        if validate and len(original) > MAX_URL_LENGTH:
            raise ValueError(SHORT_INVALID)

        if short:

            if validate and len(short) > MAX_SHORT_LENGTH:
                raise ValueError(SHORT_INVALID)

            if validate and not re.fullmatch(SHORT_REGEX_PATTERN, short):
                raise ValueError(SHORT_INVALID)

            if short in RESERVED_SHORTS:
                raise ValueError(SHORT_EXISTS)

            if URLMap.get(short):
                raise ValueError(SHORT_EXISTS)

        else:
            short = URLMap._generate_unique_short()

        url_map = URLMap(original=original, short=short)
        db.session.add(url_map)

        if commit:
            db.session.commit()

        return url_map

    @staticmethod
    def _generate_unique_short():
        """Генерирует уникальный короткий идентификатор."""
        for _ in range(MAX_GENERATION_ATTEMPTS):
            short = ''.join(
                random.choices(SHORT_ALLOWED_CHARS, k=SHORT_LENGTH)
            )

            if short in RESERVED_SHORTS:
                continue

            if not URLMap.get(short):
                return short

        raise RuntimeError(
            f'{GENERATE_ERROR} за {MAX_GENERATION_ATTEMPTS} попыток'
        )

    def get_short_url(self):
        """Возвращает абсолютный URL короткой ссылки."""
        return url_for(REDIRECT_FOR_SHORT, short=self.short, _external=True)
