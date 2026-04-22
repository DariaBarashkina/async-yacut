import asyncio
from http import HTTPStatus
from typing import List, Optional
from urllib.parse import unquote

import aiohttp
from flask import current_app

from yacut.constants import NO_TOKEN, UPLOAD_FILE_ERROR


DISK_HOST = 'https://cloud-api.yandex.net'
DISK_URL = f'{DISK_HOST}/v1/disk/resources'
DISK_URL_UPLOAD = f'{DISK_URL}/upload'
DISK_URL_DOWNLOAD = f'{DISK_URL}/download'


def _get_auth_headers() -> dict:
    """
    Формирует заголовки авторизации для запросов к Яндекс.Диску.

    Returns:
        dict: HTTP заголовок с OAuth-токеном

    Raises:
        ValueError: если токен не задан в конфигурации приложения
    """
    token = current_app.config.get('DISK_TOKEN')
    if not token:
        raise ValueError(NO_TOKEN)

    return {'Authorization': f'OAuth {token}'}


async def async_upload_files_to_yadisk(files: Optional[List]) -> List[str]:
    """
    Асинхронно загружает список файлов на Яндекс.Диск.
    Возвращает ссылки на скачивание.

    Args:
        files (Optional[List]): список файлов из Flask-формы

    Returns:
        List[str]: список публичных ссылок на загруженные файлы
    """
    valid_files = [file for file in files if file and file.filename]

    if not valid_files:
        return []

    async with aiohttp.ClientSession() as session:
        tasks = [
            upload_file_and_get_url(session, file)
            for file in valid_files
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                raise result

        return results


async def upload_file_and_get_url(session: aiohttp.ClientSession, file) -> str:
    """
    Загружает файл на Яндекс.Диск и возвращает ссылку на скачивание.

    Args:
        session (aiohttp.ClientSession): HTTP-сессия
        file: файл из Flask request

    Returns:
        str: публичная ссылка на скачивание файла
    """
    headers = _get_auth_headers()
    filename = file.filename

    upload_url = await _get_upload_url(session, headers, filename)
    file_path = await _upload_file_content(session, upload_url, file)

    return await _get_download_url(session, headers, file_path)


async def _get_upload_url(
    session: aiohttp.ClientSession,
    headers: dict,
    filename: str
) -> str:
    """
    Получает URL для загрузки файла на Яндекс.Диск.

    Args:
        session (aiohttp.ClientSession): HTTP-сессия
        headers (dict): заголовки авторизации
        filename (str): имя файла

    Returns:
        str: URL для загрузки файла
    """
    async with session.get(
        DISK_URL_UPLOAD,
        headers=headers,
        params={
            'path': f'app:/{filename}',  # noqa: E231
            'fields': 'href'
        }
    ) as response:

        if response.status == HTTPStatus.CONFLICT:
            raise FileExistsError(
                UPLOAD_FILE_ERROR.format(filename=filename)
            )

        response.raise_for_status()
        data = await response.json()
        return data['href']


async def _upload_file_content(
    session: aiohttp.ClientSession,
    upload_url: str,
    file
) -> str:
    """
    Загружает содержимое файла по предварительно полученному URL.

    Args:
        session (aiohttp.ClientSession): HTTP-сессия
        upload_url (str): URL для загрузки
        file: файл из формы

    Returns:
        str: путь к файлу на Яндекс.Диске

    Raises:
        ValueError: если отсутствует заголовок Location
    """
    async with session.put(upload_url, data=file.read()) as response:
        response.raise_for_status()

        location = response.headers.get('Location')
        if not location:
            raise ValueError('Отсутствует заголовок Location')

        return unquote(location).replace('/disk', '')


async def _get_download_url(
    session: aiohttp.ClientSession,
    headers: dict,
    file_path: str
) -> str:
    """
    Получает публичную ссылку для скачивания загруженного файла.

    Args:
        session (aiohttp.ClientSession): HTTP-сессия
        headers (dict): заголовки авторизации
        file_path (str): путь к файлу на диске

    Returns:
        str: публичный URL скачивания
    """
    async with session.get(
        DISK_URL_DOWNLOAD,
        headers=headers,
        params={
            'path': file_path,
            'fields': 'href'
        }
    ) as response:

        response.raise_for_status()
        data = await response.json()

        return data['href']
