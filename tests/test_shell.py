"""Тесты ядра эмулятора: приглашение, заглушки, exit, ошибки."""

import getpass
import socket
import unittest

from emulator.shell import EXIT_NOT_FOUND
from helpers import make_shell, run_lines


class PromptTest(unittest.TestCase):
    """Приглашение строится из реальных данных ОС."""

    def test_prompt_uses_user_and_host(self):
        """Приглашение имеет вид username@hostname:~$."""
        shell = make_shell()
        expected = f"{getpass.getuser()}@{socket.gethostname()}:~$ "
        self.assertEqual(shell.prompt(), expected)


class StubCommandsTest(unittest.TestCase):
    """Команды-заглушки выводят имя и аргументы."""

    def test_ls_stub(self):
        """ls выводит своё имя и аргументы."""
        out, _ = run_lines(make_shell(), "ls -l /tmp")
        self.assertEqual(out, "ls: args=['-l', '/tmp']\n")

    def test_cd_stub_without_args(self):
        """cd без аргументов выводит пустой список."""
        out, _ = run_lines(make_shell(), "cd")
        self.assertEqual(out, "cd: args=[]\n")


class ErrorsTest(unittest.TestCase):
    """Обработка ошибок ввода."""

    def test_unknown_command(self):
        """Неизвестная команда даёт ошибку и код 127."""
        shell = make_shell()
        _, err = run_lines(shell, "foo bar")
        self.assertEqual(err, "foo: command not found\n")
        self.assertEqual(shell.status, EXIT_NOT_FOUND)

    def test_empty_line_is_ignored(self):
        """Пустая строка ничего не выводит."""
        out, err = run_lines(make_shell(), "")
        self.assertEqual((out, err), ("", ""))


class ExitTest(unittest.TestCase):
    """Команда exit."""

    def test_exit_with_code(self):
        """exit N завершает работу с кодом N."""
        shell = make_shell()
        run_lines(shell, "exit 3")
        self.assertFalse(shell.running)
        self.assertEqual(shell.exit_code, 3)

    def test_exit_uses_last_status(self):
        """exit без аргумента возвращает код последней команды."""
        shell = make_shell()
        run_lines(shell, "unknown", "exit")
        self.assertEqual(shell.exit_code, EXIT_NOT_FOUND)

    def test_exit_non_numeric(self):
        """Нечисловой аргумент exit — ошибка, работа продолжается."""
        shell = make_shell()
        _, err = run_lines(shell, "exit abc")
        self.assertIn("numeric argument required", err)
        self.assertTrue(shell.running)

    def test_exit_too_many_args(self):
        """Лишние аргументы exit — ошибка."""
        shell = make_shell()
        _, err = run_lines(shell, "exit 1 2")
        self.assertIn("too many arguments", err)
        self.assertTrue(shell.running)


if __name__ == "__main__":
    unittest.main()
