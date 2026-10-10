"""Тесты парсера командной строки."""

import unittest

from emulator.parser import parse_line


class ParseLineTest(unittest.TestCase):
    """Проверки разбиения строки на команду и аргументы."""

    def test_command_and_args(self):
        """Команда и аргументы разделяются по пробелам."""
        self.assertEqual(parse_line("ls -l /home"), ["ls", "-l", "/home"])

    def test_multiple_spaces(self):
        """Повторяющиеся пробелы не создают пустых аргументов."""
        self.assertEqual(parse_line("  cd    dir  "), ["cd", "dir"])

    def test_byte_order_mark_is_removed(self):
        """BOM в начале строки не попадает в имя команды."""
        self.assertEqual(parse_line("﻿ls"), ["ls"])

    def test_empty_line(self):
        """Пустая строка даёт пустой список."""
        self.assertEqual(parse_line("   "), [])


if __name__ == "__main__":
    unittest.main()
