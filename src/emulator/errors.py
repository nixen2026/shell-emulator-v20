"""Коды завершения и исключения для сообщения о результате команд."""

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_NOT_FOUND = 127


class ShellError(Exception):
    """Ошибка выполнения команды; текст выводится пользователю."""


class ExitRequest(Exception):
    """Запрос на завершение работы эмулятора с заданным кодом."""

    def __init__(self, code):
        """Сохранить код завершения процесса эмулятора."""
        super().__init__(code)
        self.code = code
