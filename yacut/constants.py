import string

# Длины полей
SHORT_LENGTH = 6
MAX_SHORT_LENGTH = 16
MAX_URL_LENGTH = 2048
MAX_GENERATION_ATTEMPTS = 10

# Допустимые символы для короткой ссылки
SHORT_ALLOWED_CHARS = string.ascii_letters + string.digits
SHORT_REGEX_PATTERN = f'^[{SHORT_ALLOWED_CHARS}]+$'

# Зарезервированные имена
RESERVED_SHORTS = {'files'}

# Яндекс.Диск
YANDEX_UPLOAD_PATH = '/disk/resources/upload'
YANDEX_DOWNLOAD_PATH = '/disk/resources/download'

# Имя эндпоинта для редиректа
REDIRECT_FOR_SHORT = 'redirect_view'

# Ошибки API
EMPTY_BODY = 'Отсутствует тело запроса'
URL_REQUIRED = '"url" является обязательным полем!'
INVALID_URL = 'Указан недопустимый URL'
URL_TOO_LONG = 'Длина URL превышает допустимую'
SHORT_EXISTS = 'Предложенный вариант короткой ссылки уже существует.'
SHORT_INVALID = 'Указано недопустимое имя для короткой ссылки'
NOT_FOUND = 'Указанный id не найден'
RESOURCE_NOT_FOUND = 'Ресурс не найден'
INTERNAL_ERROR = 'Внутренняя ошибка сервера'
GENERATE_ERROR = (
    'Не удалось сгенерировать уникальный short. '
    'Число попыток - '
    f'{MAX_GENERATION_ATTEMPTS}'
)
# Ошибки форм
REQUIRED_FIELD = 'Обязательное поле'
INVALID_URL_FORM = 'Некорректный URL'
ONLY_LATIN_AND_DIGITS = 'Только латинские буквы и цифры'
SHORT_MAX_LENGTH_ERROR = f'Допустимо символов: не более {MAX_SHORT_LENGTH}'

# Сообщения для загрузки файлов
CHOOSE_FILES = 'Выберите хотя бы один файл'
NO_FILES = 'Выберите файлы для загрузки'
NO_TOKEN = 'Токен Яндекс.Диска не задан'
FILES_UPLOADED = 'Файлы успешно загружены'
UPLOAD_LINK_ERROR = 'Ошибка получения ссылки для загрузки {filename}'
UPLOAD_FILE_ERROR = 'Ошибка загрузки файла {filename}'
LOCATION_HEADER_ERROR = 'Отсутствует заголовок Location'

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
