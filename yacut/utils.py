import random
import aiohttp
import asyncio
from flask import current_app
from yacut.models import URLMap


def generate_short_id(length=None):
    if length is None:
        length = current_app.config['SHORT_ID_LENGTH']
    chars = current_app.config['ALLOWED_CHARS']
    return ''.join(random.choices(chars, k=length))


def get_unique_short_id():
    while True:
        short = generate_short_id()
        if not URLMap.query.filter_by(short=short).first():
            return short


async def upload_single_file(session, file_storage, token):
    filename = file_storage.filename
    headers = {'Authorization': f'OAuth {token}'}
    upload_url_api = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    params = {'path': f'app:/{filename}', 'overwrite': 'true'}  # noqa: E231
    async with session.get(
        upload_url_api, headers=headers, params=params
    ) as resp:
        if resp.status != 200:
            raise Exception(
                f'Ошибка получения ссылки для загрузки: {resp.status}'
            )
        data = await resp.json()
        upload_url = data['href']

    file_content = file_storage.read()
    async with session.put(upload_url, data=file_content) as resp:
        if resp.status not in (200, 201):
            raise Exception(f'Ошибка загрузки файла: {resp.status}')

    file_path = f'app:/{filename}'  # noqa: E231
    return filename, file_path


async def upload_files_to_disk(files, token):
    async with aiohttp.ClientSession() as session:
        tasks = [upload_single_file(session, f, token) for f in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


def process_uploaded_files(files):
    token = current_app.config['DISK_TOKEN']
    if not token:
        raise ValueError('Токен Яндекс.Диска не задан')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        results = loop.run_until_complete(upload_files_to_disk(files, token))
    finally:
        loop.close()
    return results
