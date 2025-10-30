class TelegramParserException(Exception):
    """Базовое исключение для парсера Telegram"""

    pass


class ChannelNotFoundException(TelegramParserException):
    """Канал не найден"""

    pass


class AuthenticationException(TelegramParserException):
    """Ошибка аутентификации Telegram"""

    pass


class RateLimitException(TelegramParserException):
    """Превышен лимит запросов"""

    pass
