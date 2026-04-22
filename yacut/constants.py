import string


import string

# Длины полей
SHORT_LENGTH = 6
MAX_SHORT_LENGTH = 16
MAX_URL_LENGTH = 2048
MAX_GENERATION_ATTEMPTS = 10

# Допустимые символы
ALLOWED_CHARS = string.ascii_letters + string.digits
REGEX_PATTERN = f'^[{ALLOWED_CHARS}]*$'

# Зарезервированные имена
RESERVED_SHORTS = {'files'}

# URL API Яндекс.Диска
YANDEX_UPLOAD_URL = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
YANDEX_DOWNLOAD_URL = 'https://cloud-api.yandex.net/v1/disk/resources/download'

# Имя эндпоинта для редиректа
REDIRECT_FOR_SHORT = 'redirect_view'

# Ошибки API
EMPTY_BODY = 'Отсутствует тело запроса'
URL_REQUIRED = '"url" является обязательным полем!'
INVALID_URL = 'Указан недопустимый URL'
SHORT_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
SHORT_INVALID = 'Указано недопустимое имя для короткой ссылки'
NOT_FOUND = 'Указанный id не найден'
RESOURCE_NOT_FOUND = 'Ресурс не найден'
INTERNAL_ERROR = 'Внутренняя ошибка сервера'

# Ошибки форм
REQUIRED_FIELD = 'Обязательное поле'
INVALID_URL_FORM = 'Некорректный URL'
ONLY_LATIN_AND_DIGITS = 'Только латинские буквы и цифры'
SHORT_MAX_LENGTH = f'Не более {MAX_SHORT_LENGTH} символов'

# Сообщения для загрузки файлов
CHOOSE_FILES = 'Выберите хотя бы один файл'
NO_FILES = 'Выберите файлы для загрузки'
NO_TOKEN = 'Токен Яндекс.Диска не задан'
FILES_UPLOADED = 'Файлы успешно загружены'
UPLOAD_LINK_ERROR = 'Ошибка получения ссылки для загрузки {filename}'
UPLOAD_FILE_ERROR = 'Ошибка загрузки файла {filename}'

# Успешные сообщения
SHORT_LINK_READY = 'Ваша короткая ссылка:'

# Общие ошибки
ERROR_GENERIC = 'Ошибка: {error}'
ERROR_UPLOAD = 'Ошибка загрузки файла: {field}'

# Тексты полей форм
LABEL_LONG_LINK = 'Длинная ссылка'
LABEL_SHORT_LINK = 'Ваш вариант короткой ссылки'
LABEL_CHOOSE_FILES = 'Выберите файлы'

# Тексты кнопок
BTN_CREATE = 'Создать'
BTN_UPLOAD = 'Загрузить'
