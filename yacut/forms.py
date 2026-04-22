from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from flask_wtf.file import MultipleFileField

from yacut.constants import (
    ALLOWED_CHARS,
    BTN_CREATE,
    BTN_UPLOAD,
    CHOOSE_FILES,
    LABEL_CHOOSE_FILES,
    LABEL_LONG_LINK,
    LABEL_SHORT_LINK,
    MAX_SHORT_LENGTH,
    MAX_URL_LENGTH,
    ONLY_LATIN_AND_DIGITS,
    REQUIRED_FIELD,
    RESERVED_SHORTS,
    SHORT_EXISTS,
)
from yacut.models import URLMap


class URLMapForm(FlaskForm):
    """Форма для создания короткой ссылки."""

    original_link = URLField(
        LABEL_LONG_LINK,
        validators=[
            DataRequired(message=REQUIRED_FIELD),
            Length(max=MAX_URL_LENGTH)
        ]
    )

    custom_id = StringField(
        LABEL_SHORT_LINK,
        validators=[
            Optional(),
            Length(max=MAX_SHORT_LENGTH),
        ]
    )

    submit = SubmitField(BTN_CREATE)

    def validate_custom_id(self, field):
        """Валидация пользовательского короткого идентификатора."""
        if not field.data:
            return

        short = field.data

        if short in RESERVED_SHORTS:
            raise ValidationError(SHORT_EXISTS)

        if not all(c in ALLOWED_CHARS for c in short):
            raise ValidationError(ONLY_LATIN_AND_DIGITS)

        if URLMap.get(short):
            raise ValidationError(SHORT_EXISTS)


class UploadForm(FlaskForm):
    """Форма для загрузки файлов."""

    files = MultipleFileField(
        LABEL_CHOOSE_FILES,
        validators=[
            DataRequired(message=CHOOSE_FILES)
        ]
    )

    submit = SubmitField(BTN_UPLOAD)
