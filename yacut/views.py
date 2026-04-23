from http import HTTPStatus

from flask import abort, flash, redirect, render_template

from yacut import app
from yacut.constants import (
    REDIRECT_FOR_SHORT,
    ERROR_GENERIC,
    ERROR_UPLOAD
)
from yacut.forms import UploadForm, URLMapForm
from yacut.models import URLMap
from yacut.disk import async_upload_files_to_yadisk


@app.route('/<short>', endpoint=REDIRECT_FOR_SHORT)
def redirect_view(short):
    """Редирект по короткой ссылке."""
    url_map = URLMap.get(short)

    if url_map is None:
        abort(HTTPStatus.NOT_FOUND)

    return redirect(url_map.original)


@app.route('/', methods=('GET', 'POST'))
def index_view():
    form = URLMapForm()

    if not form.validate_on_submit():
        return render_template('index.html', form=form)

    try:
        url_map = URLMap.create(
            original=form.original_link.data,
            short=form.custom_id.data,
            validate=False
        )
    except (ValueError, RuntimeError) as error:
        flash(ERROR_GENERIC.format(error=error))
        return render_template('index.html', form=form)

    return render_template(
        'index.html',
        form=form,
        short=url_map.get_short_url()
    )


@app.route('/files', methods=('GET', 'POST'))
async def files_view():
    form = UploadForm()
    template = 'download_files.html'

    if not form.validate_on_submit():
        return render_template(template, form=form)

    try:
        urls = await async_upload_files_to_yadisk(form.files.data)
    except Exception as error:
        flash(ERROR_UPLOAD.format(field=error))
        return render_template(template, form=form)

    try:
        short_for_downloads = [
            {
                'filename': file_obj.filename,
                'short': URLMap.create(original=original_url).get_short_url()
            }
            for file_obj, original_url in zip(form.files.data, urls)
        ]
    except (ValueError, RuntimeError) as error:
        flash(ERROR_UPLOAD.format(field=error))
        return render_template(template, form=form)

    return render_template(
        template,
        form=form,
        short_for_downloads=short_for_downloads
    )
