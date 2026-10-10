"""Тесты параметров командной строки, conf-dump и стартовых скриптов."""

import os
import tempfile
import unittest

from emulator.config import NOT_SET, Config, parse_args
from emulator.parser import parse_line
from helpers import make_shell, run_lines


class ParseArgsTest(unittest.TestCase):
    """Разбор параметров командной строки."""

    def test_defaults(self):
        """Без параметров пути не заданы."""
        self.assertEqual(parse_args([]), Config())

    def test_all_options(self):
        """Оба параметра сохраняются в Config."""
        config = parse_args(["--vfs", "fs.zip", "--script", "s.txt"])
        self.assertEqual(config, Config("fs.zip", "s.txt"))

    def test_unknown_option(self):
        """Неизвестный параметр завершает процесс с ошибкой."""
        with self.assertRaises(SystemExit):
            parse_args(["--bad"])


class ConfDumpTest(unittest.TestCase):
    """Служебная команда conf-dump."""

    def test_dump_values(self):
        """conf-dump выводит параметры в формате ключ=значение."""
        shell = make_shell(config=Config("fs.zip", None))
        out, _ = run_lines(shell, "conf-dump")
        self.assertEqual(out, f"vfs=fs.zip\nscript={NOT_SET}\n")

    def test_dump_with_args(self):
        """conf-dump не принимает аргументов."""
        _, err = run_lines(make_shell(), "conf-dump x")
        self.assertEqual(err, "conf-dump: too many arguments\n")


class CommentsTest(unittest.TestCase):
    """Комментарии в синтаксисе Python."""

    def test_full_line_comment(self):
        """Строка-комментарий пуста для парсера."""
        self.assertEqual(parse_line("# comment"), [])

    def test_trailing_comment(self):
        """Комментарий в конце строки отбрасывается."""
        self.assertEqual(parse_line("ls a # b c"), ["ls", "a"])


class ScriptTest(unittest.TestCase):
    """Выполнение стартового скрипта."""

    def run_script_text(self, text):
        """Записать скрипт во временный файл, выполнить, вернуть shell."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "start.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write(text)
            shell = make_shell()
            self.assertTrue(shell.run_script(path))
        return shell

    def test_echo_input_and_output(self):
        """Скрипт отображает приглашение, ввод и вывод."""
        shell = self.run_script_text("# comment\n\nls a\n")
        expected = f"{shell.prompt()}ls a\nls: args=['a']\n"
        self.assertEqual(shell.out.getvalue(), expected)

    def test_error_reported_with_line(self):
        """Ошибка в скрипте сообщается с номером строки."""
        shell = self.run_script_text("ls\nbad\nls\n")
        err = shell.err.getvalue()
        self.assertIn("bad: command not found", err)
        self.assertIn(":2: error: command exited with status 127", err)
        self.assertEqual(shell.out.getvalue().count("ls: args"), 2)

    def test_exit_stops_script(self):
        """exit в скрипте прекращает его выполнение."""
        shell = self.run_script_text("exit 4\nls\n")
        self.assertFalse(shell.running)
        self.assertEqual(shell.exit_code, 4)
        self.assertNotIn("ls: args", shell.out.getvalue())

    def test_missing_script(self):
        """Отсутствующий файл скрипта — ошибка."""
        shell = make_shell()
        self.assertFalse(shell.run_script("no/such/script.txt"))
        self.assertIn("cannot read", shell.err.getvalue())


if __name__ == "__main__":
    unittest.main()
