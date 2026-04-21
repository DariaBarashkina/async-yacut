from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField
from wtforms.validators import (DataRequired, Length, Optional, Regexp,
                                ValidationError)

from yacut.models import URLMap
from yacut.settings import Config


class URLForm(FlaskForm):
    original_link = StringField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            Length(max=2048)
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(
                max=Config.MAX_CUSTOM_ID_LENGTH,
                message='Не более 16 символов'
            ),
            Regexp(
                r'^[A-Za-z0-9]*$',
                message='Только латинские буквы и цифры'
            )
        ]
    )
    submit = SubmitField('Создать')

    def validate_original_link(self, field):
        if not (
            field.data.startswith('http://')
            or field.data.startswith('https://')
        ):
            raise ValidationError('Некорректный URL')

    def validate_custom_id(self, field):
        if field.data:
            if field.data == 'files':
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
            if URLMap.query.filter_by(short=field.data).first():
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )


class UploadFilesForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы',
        validators=[DataRequired(message='Выберите хотя бы один файл')]
    )
    submit = SubmitField('Загрузить')
