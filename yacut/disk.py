import asyncio
from http import HTTPStatus
from typing import List, Optional
from urllib.parse import unquote

import aiohttp
from flask import current_app

from yacut.constants import (
    NO_TOKEN,
    UPLOAD_FILE_ERROR,
    YANDEX_UPLOAD_PATH,
    YANDEX_DOWNLOAD_PATH,
    LOCATION_HEADER_ERROR,
)

# --- "константы модуля" ---
UPLOAD_URL = "{base}" + YANDEX_UPLOAD_PATH
DOWNLOAD_URL = "{base}" + YANDEX_DOWNLOAD_PATH
AUTH_HEADER = 'Authorization'
AUTH_HEADER_VALUE = 'OAuth {token}'


async def async_upload_files_to_yadisk(files: Optional[List]) -> List[str]:
    """Асинхронно загружает список файлов на Яндекс.Диск."""
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[
                upload_file_and_get_url(session, file)
                for file in files
            ]
        )


async def upload_file_and_get_url(
    session: aiohttp.ClientSession,
    file
) -> str:
    """Загружает файл и возвращает ссылку для скачивания."""

    token = current_app.config.get('DISK_TOKEN')
    if not token:
        raise ValueError(NO_TOKEN)

    filename = file.filename

    headers = {
        AUTH_HEADER: AUTH_HEADER_VALUE.format(token=token)
    }

    base = current_app.config['YANDEX_API_BASE']

    upload_url = await _get_upload_url(session, headers, base, filename)
    file_path = await _upload_file_content(session, upload_url, file)

    return await _get_download_url(session, headers, base, file_path)


async def _get_upload_url(
    session: aiohttp.ClientSession,
    headers: dict,
    base: str,
    filename: str
) -> str:
    """Получает URL для загрузки файла."""

    async with session.get(
        UPLOAD_URL.format(base=base),
        headers=headers,
        params={
            'path': f'app:/{filename}',    # noqa: E231
            'fields': 'href'
        }
    ) as response:

        if response.status == HTTPStatus.CONFLICT:
            raise FileExistsError(
                UPLOAD_FILE_ERROR.format(filename=filename)
            )

        response.raise_for_status()
        return (await response.json())['href']


async def _upload_file_content(
    session: aiohttp.ClientSession,
    upload_url: str,
    file
) -> str:
    """Загружает файл на Яндекс.Диск."""

    async with session.put(upload_url, data=file.read()) as response:
        response.raise_for_status()

        location = (
            response.headers.get('Location')
            or response.headers.get('location')
        )

        if not location:
            raise ValueError(LOCATION_HEADER_ERROR)

        return unquote(location).replace('/disk', '')


async def _get_download_url(
    session: aiohttp.ClientSession,
    headers: dict,
    base: str,
    file_path: str
) -> str:
    """Получает ссылку для скачивания файла."""

    async with session.get(
        DOWNLOAD_URL.format(base=base),
        headers=headers,
        params={
            'path': file_path,
            'fields': 'href'
        }
    ) as response:

        response.raise_for_status()
        return (await response.json())['href']
