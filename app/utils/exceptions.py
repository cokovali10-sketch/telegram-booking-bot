class AppError(Exception):
    """Базовая ошибка приложения."""

    def __init__(self, message: str, user_message: str | None = None) -> None:
        super().__init__(message)
        self.user_message = user_message or message


class ValidationError(AppError):
    """Ошибка валидации пользовательского ввода."""


class DatabaseError(AppError):
    """Ошибка работы с базой данных."""


class NotFoundError(AppError):
    """Запрашиваемая сущность не найдена."""
