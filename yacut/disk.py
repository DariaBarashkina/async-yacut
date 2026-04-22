import asyncio
from http import HTTPStatus
from typing import List, Optional
from urllib.parse import unquote

import aiohttp
from flask import current_app

from yacut.constants import (
    NO_TOKEN,
    UPLOAD_FILE_ERROR,
)


DISK_HOST = 'https://cloud-api.yandex.net'
DISK_URL = f'{DISK_HOST}/v1/disk/resources/'
DISK_URL_UPLOAD = f'{DISK_URL}upload'
DISK_URL_DOWNLOAD = f'{DISK_URL}download'


def _get_auth_headers():
    """Возвращает заголовки авторизации."""
    token = current_app.config.get('DISK_TOKEN')
    if not token:
        raise ValueError(NO_TOKEN)
    return {'Authorization': f'OAuth {token}'}


async def async_upload_files_to_yadisk(files: Optional[List]):
    """
    Асинхронно загружает несколько файлов на Яндекс.Диск.

    Args:
        files: Список объектов файлов из формы.

    Returns:
        Список URL для скачивания загруженных файлов.
    """
    valid_files = [f for f in files if f.filename]
    if not valid_files:
        return []

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(upload_file_and_get_url(session, file))
            for file in valid_files
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                raise result

        return results


async def upload_file_and_get_url(session: aiohttp.ClientSession, file) -> str:
    """
    Загружает файл на Яндекс.Диск и возвращает публичную ссылку для скачивания.
    """
    headers = _get_auth_headers()
    filename = file.filename
    upload_url = await _get_upload_url(session, headers, filename)
    file_path = await _upload_file_content(session, upload_url, file)
    return await _get_download_url(session, headers, file_path)


async def _get_upload_url(
    session: aiohttp.ClientSession, headers: dict, filename: str
) -> str:
    """Получает предопределённый URL для загрузки файла."""
    async with session.get(
        DISK_URL_UPLOAD,
        headers=headers,
        params={'path': f'app:/{filename}', 'fields': 'href'},  # noqa: E231
    ) as response:
        if response.status == HTTPStatus.CONFLICT:
            raise FileExistsError(
                UPLOAD_FILE_ERROR.format(filename=filename)
            )
        response.raise_for_status()
        return (await response.json())['href']


async def _upload_file_content(
    session: aiohttp.ClientSession, upload_url: str, file
) -> str:
    """Выполняет загрузку содержимого файла на указанный URL."""
    async with session.put(upload_url, data=file.read()) as response:
        response.raise_for_status()
        location_header = response.headers.get('Location')
        if not location_header:
            raise ValueError('Отсутствует заголовок Location')
        return unquote(location_header).replace('/disk', '')


async def _get_download_url(
    session: aiohttp.ClientSession, headers: dict, file_path: str
) -> str:
    """Получает публичную ссылку для скачивания файла."""
    async with session.get(
        DISK_URL_DOWNLOAD,
        headers=headers,
        params={'path': file_path, 'fields': 'href'},
    ) as response:
        response.raise_for_status()
        return (await response.json())['href']
