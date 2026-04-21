import aiohttp
import requests
from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)
from markupsafe import Markup

from yacut import app, db
from yacut.forms import UploadFilesForm, URLForm
from yacut.models import URLMap
from yacut.utils import get_unique_short_id


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLForm()
    if form.validate_on_submit():
        custom_id = form.custom_id.data
        if not custom_id:
            custom_id = get_unique_short_id()
        url_map = URLMap(original=form.original_link.data, short=custom_id)
        db.session.add(url_map)
        db.session.commit()
        short_url = f'{request.host_url}{custom_id}'
        flash(
            Markup(
                f'Ваша короткая ссылка: <a href="{short_url}">{short_url}</a>'
            ),
            'success'
        )
        return render_template('index.html', form=form)
    return render_template('index.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = UploadFilesForm()
    results = []
    if form.validate_on_submit():
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            flash('Выберите файлы для загрузки', 'danger')
            return redirect(url_for('files_view'))

        token = current_app.config['DISK_TOKEN']
        if not token:
            flash('Токен Яндекс.Диска не задан', 'danger')
            return redirect(url_for('files_view'))

        headers = {'Authorization': f'OAuth {token}'}
        async with aiohttp.ClientSession() as session:
            for file_storage in files:
                filename = file_storage.filename

                upload_url_api = (
                    'https://cloud-api.yandex.net/v1/disk/resources/upload'
                )
                params = {
                    'path': f'app:/{filename}',  # noqa: E231
                    'overwrite': 'true'
                }
                async with session.get(
                    upload_url_api, headers=headers, params=params
                ) as resp:
                    if resp.status != 200:
                        flash(
                            f'Ошибка получения ссылки для загрузки {filename}',
                            'danger'
                        )
                        continue
                    data = await resp.json()
                    upload_url = data['href']

                file_content = file_storage.read()
                async with session.put(upload_url, data=file_content) as resp:
                    if resp.status not in (200, 201):
                        flash(f'Ошибка загрузки файла {filename}', 'danger')
                        continue

                download_url_api = (
                    'https://cloud-api.yandex.net/v1/disk/resources/download'
                )
                async with session.get(
                    download_url_api,
                    headers=headers,
                    params={'path': f'app:/{filename}'}  # noqa: E231
                ) as _:
                    pass

                file_path = f'app:/{filename}'  # noqa: E231
                short = get_unique_short_id()
                url_map = URLMap(original=file_path, short=short)
                db.session.add(url_map)
                db.session.commit()
                results.append({
                    'filename': filename,
                    'short_url': f'{request.host_url}{short}'
                })

        flash('Файлы успешно загружены', 'success')
    return render_template('files.html', form=form, results=results)


@app.route('/<string:short_id>')
def redirect_view(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()
    original = url_map.original

    if original.startswith('app:/'):
        token = current_app.config['DISK_TOKEN']
        headers = {'Authorization': f'OAuth {token}'}
        download_url_api = (
            'https://cloud-api.yandex.net/v1/disk/resources/download'
        )
        try:
            response = requests.get(
                download_url_api,
                headers=headers,
                params={'path': original},
                timeout=10
            )
            response.raise_for_status()
            download_link = response.json()['href']
            filename = original.replace('app:/', '')
            return render_template(
                'download.html',
                download_link=download_link,
                filename=filename
            )
        except Exception as e:
            current_app.logger.error(f'Ошибка получения ссылки: {e}')
            abort(500)
    else:
        return redirect(original)
