"""Ядро эмулятора: приглашение к вводу, выполнение команд и REPL."""

import getpass
import socket
import sys

from emulator.commands import COMMANDS
from emulator.errors import ExitRequest, ShellError
from emulator.parser import parse_line

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EXIT_NOT_FOUND = 127
DEFAULT_USERNAME = "user"


def get_username():
    """Вернуть имя текущего пользователя реальной ОС."""
    try:
        return getpass.getuser()
    except (KeyError, OSError):
        return DEFAULT_USERNAME


class Shell:
    """Состояние и цикл работы эмулятора оболочки."""

    def __init__(self, out=None, err=None):
        """Создать эмулятор, пишущий в потоки ``out`` и ``err``."""
        self.out = out or sys.stdout
        self.err = err or sys.stderr
        self.username = get_username()
        self.hostname = socket.gethostname()
        self.status = EXIT_SUCCESS
        self.running = True
        self.exit_code = EXIT_SUCCESS

    def prompt(self):
        """Сформировать приглашение вида ``username@hostname:~$``."""
        return f"{self.username}@{self.hostname}:~$ "

    def write(self, text):
        """Вывести строку в стандартный поток вывода."""
        self.out.write(text + "\n")
        self.out.flush()

    def error(self, text):
        """Вывести сообщение об ошибке в поток ошибок."""
        self.err.write(text + "\n")
        self.err.flush()

    def execute(self, line):
        """Выполнить одну строку ввода и вернуть код завершения."""
        words = parse_line(line)
        if not words:
            return self.status
        name, args = words[0], words[1:]
        command = COMMANDS.get(name)
        if command is None:
            self.error(f"{name}: command not found")
            self.status = EXIT_NOT_FOUND
            return self.status
        try:
            command(self, args)
            self.status = EXIT_SUCCESS
        except ShellError as exc:
            self.error(str(exc))
            self.status = EXIT_FAILURE
        except ExitRequest as request:
            self.running = False
            self.exit_code = request.code
        return self.status

    def repl(self):
        """Интерактивный цикл «чтение — выполнение — вывод».

        Возвращает код завершения эмулятора.
        """
        while self.running:
            try:
                line = input(self.prompt())
            except EOFError:
                self.write("")
                break
            except KeyboardInterrupt:
                self.write("")
                continue
            self.execute(line)
        return self.exit_code
