import random
from datetime import datetime

from flask import url_for

from yacut import db
from yacut.constants import (
    ALLOWED_CHARS,
    MAX_GENERATION_ATTEMPTS,
    RESERVED_SHORTS,
    SHORT_LENGTH,
)


class URLMap(db.Model):
    """Модель для хранения соответствия оригинальной и короткой ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String, nullable=False)
    short = db.Column(db.String, unique=True, nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def get(cls, short):
        """Возвращает запись по короткому идентификатору."""
        return cls.query.filter_by(short=short).first()

    @classmethod
    def create(cls, original, short=None):
        """Создаёт новую запись в БД."""
        if short:
            cls._validate_short(short)
        else:
            short = cls._generate_unique_short()

        obj = cls(original=original, short=short)
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def _generate_unique_short(cls):
        """Генерирует уникальный короткий идентификатор."""
        for _ in range(MAX_GENERATION_ATTEMPTS):
            short = ''.join(random.choices(ALLOWED_CHARS, k=SHORT_LENGTH))
            if not cls.get(short) and short not in RESERVED_SHORTS:
                return short
        raise RuntimeError('Не удалось сгенерировать уникальный short')

    @classmethod
    def _validate_short(cls, short):
        """Проверяет, что short допустим и не занят."""
        if short in RESERVED_SHORTS:
            raise ValueError(
                'Предложенный вариант короткой ссылки уже существует.'
            )
        if cls.get(short):
            raise ValueError(
                'Предложенный вариант короткой ссылки уже существует.'
            )

    def get_short_url(self):
        """Возвращает полный URL короткой ссылки."""
        return url_for('redirect_view', short=self.short, _external=True)
