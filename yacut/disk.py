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
)

LOCATION_HEADER_ERROR = 'Отсутствует заголовок Location'


def _get_headers():
    token = current_app.config.get('DISK_TOKEN')
    if not token:
        raise ValueError(NO_TOKEN)
    return {'Authorization': f'OAuth {token}'}


async def async_upload_files_to_yadisk(files: Optional[List]) -> List[str]:
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(
            *[
                upload_file_and_get_url(session, file)
                for file in files if file.filename
            ]
        )


async def upload_file_and_get_url(
    session: aiohttp.ClientSession,
    file
) -> str:
    headers = _get_headers()
    filename = file.filename

    upload_url = await _get_upload_url(session, headers, filename)
    file_path = await _upload_file_content(session, upload_url, file)

    return await _get_download_url(session, headers, file_path)


async def _get_upload_url(
    session: aiohttp.ClientSession,
    headers: dict,
    filename: str
) -> str:
    base = current_app.config['YANDEX_API_BASE']

    async with session.get(
        f"{base}{YANDEX_UPLOAD_PATH}",
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
    file_path: str
) -> str:
    base = current_app.config['YANDEX_API_BASE']

    async with session.get(
        f"{base}{YANDEX_DOWNLOAD_PATH}",
        headers=headers,
        params={
            'path': file_path,
            'fields': 'href'
        }
    ) as response:

        response.raise_for_status()
        return (await response.json())['href']
