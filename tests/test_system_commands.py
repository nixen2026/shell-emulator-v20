"""Тесты команд clear и uname."""

import platform
import unittest

from emulator.terminal import CLEAR_SEQUENCE
from helpers import make_shell, run_lines


class ClearTest(unittest.TestCase):
    """Команда clear."""

    def test_clear(self):
        """clear выводит ANSI-последовательность очистки экрана."""
        out, _ = run_lines(make_shell(), "clear")
        self.assertEqual(out, CLEAR_SEQUENCE)

    def test_clear_with_args(self):
        """clear не принимает аргументов."""
        _, err = run_lines(make_shell(), "clear x")
        self.assertEqual(err, "clear: too many arguments\n")


class UnameTest(unittest.TestCase):
    """Команда uname выводит данные реальной ОС."""

    def setUp(self):
        """Получить сведения о реальной ОС."""
        self.info = platform.uname()

    def test_default(self):
        """Без опций выводится имя ядра (системы)."""
        out, _ = run_lines(make_shell(), "uname")
        self.assertEqual(out, f"{self.info.system}\n")

    def test_combined_options(self):
        """Опции можно объединять: -sn и -s -m."""
        out, _ = run_lines(make_shell(), "uname -sn", "uname -m -s")
        info = self.info
        self.assertEqual(out, f"{info.system} {info.node}\n"
                              f"{info.system} {info.machine}\n")

    def test_all(self):
        """-a выводит все поля."""
        out, _ = run_lines(make_shell(), "uname -a")
        info = self.info
        expected = " ".join([info.system, info.node, info.release,
                             info.version, info.machine])
        self.assertEqual(out, expected + "\n")

    def test_errors(self):
        """Неизвестная опция и лишний операнд — ошибки."""
        _, err = run_lines(make_shell(), "uname -x", "uname foo")
        self.assertEqual(err.splitlines(), [
            "uname: invalid option -- 'x'",
            "uname: extra operand 'foo'",
        ])


if __name__ == "__main__":
    unittest.main()
