"""Ядро эмулятора: приглашение к вводу, выполнение команд и REPL."""

import getpass
import socket
import sys

from emulator.commands import COMMANDS
from emulator.config import Config
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

    def __init__(self, config=None, out=None, err=None):
        """Создать эмулятор с настройками ``config``.

        Вывод пишется в поток ``out``, ошибки — в поток ``err``.
        """
        self.config = config or Config()
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

    def print_debug_config(self):
        """Отладочный вывод всех параметров, заданных при запуске."""
        for line in self.config.dump():
            self.write(f"[debug] {line}")

    def run_script(self, path):
        """Выполнить стартовый скрипт, имитируя диалог с пользователем.

        Перед выполнением каждой команды выводится приглашение и сама
        команда. Строки-комментарии и пустые строки пропускаются.
        Возвращает False, если файл скрипта не удалось прочитать.
        """
        try:
            with open(path, encoding="utf-8-sig") as file:
                lines = file.read().splitlines()
        except OSError as exc:
            self.error(f"script: cannot read '{path}': {exc.strerror}")
            return False
        for number, line in enumerate(lines, start=1):
            if not self.running:
                break
            self.run_script_line(path, number, line)
        return True

    def run_script_line(self, path, number, line):
        """Выполнить строку скрипта и сообщить об ошибке с её номером."""
        if not parse_line(line):
            return
        self.write(self.prompt() + line)
        status = self.execute(line)
        if self.running and status != EXIT_SUCCESS:
            self.error(f"{path}:{number}: error: "
                       f"command exited with status {status}")

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
