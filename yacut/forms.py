from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    ValidationError,
    Regexp
)

from yacut.constants import (
    SHORT_REGEX_PATTERN,
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
            Regexp(SHORT_REGEX_PATTERN, message=ONLY_LATIN_AND_DIGITS)
        ]
    )

    submit = SubmitField(BTN_CREATE)

    def validate_custom_id(self, field):
        if field.data in RESERVED_SHORTS or URLMap.get(field.data) is not None:
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
