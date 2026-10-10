"""Тесты команд ls и cd, работающих с VFS."""

import unittest

from emulator.errors import EXIT_FAILURE
from emulator.vfs import resolve_parts
from helpers import make_shell, make_vfs, run_lines


def deep_shell():
    """Создать эмулятор с тестовой VFS из нескольких уровней."""
    return make_shell(vfs=make_vfs())


class ResolvePartsTest(unittest.TestCase):
    """Вычисление абсолютных путей."""

    def test_variants(self):
        """Абсолютные, относительные, домашние пути, . и .."""
        cwd = ["docs", "notes"]
        cases = {
            "/src": ["src"],
            "archive": ["docs", "notes", "archive"],
            "..": ["docs"],
            "../../..": [],
            "./archive/../.": ["docs", "notes"],
            "~": [],
            "~/src": ["src"],
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                self.assertEqual(resolve_parts(cwd, path), expected)


class LsTest(unittest.TestCase):
    """Команда ls."""

    def test_current_dir(self):
        """Без аргументов выводится текущий каталог (сортировка)."""
        out, _ = run_lines(deep_shell(), "ls")
        self.assertEqual(out, "README.txt  docs  empty  src\n")

    def test_directory_argument(self):
        """Содержимое каталога по пути."""
        out, _ = run_lines(deep_shell(), "ls docs/notes")
        self.assertEqual(out, "archive  todo.txt\n")

    def test_empty_directory(self):
        """Пустой каталог ничего не выводит."""
        out, err = run_lines(deep_shell(), "ls empty")
        self.assertEqual((out, err), ("", ""))

    def test_file_argument(self):
        """Для файла выводится его путь."""
        out, _ = run_lines(deep_shell(), "ls docs/guide.txt")
        self.assertEqual(out, "docs/guide.txt\n")

    def test_long_format(self):
        """ls -l выводит тип, размер и имя."""
        out, _ = run_lines(deep_shell(), "ls -l docs")
        self.assertEqual(
            out, "-        6 guide.txt\nd        2 notes\n")

    def test_several_paths(self):
        """Несколько путей: сначала файлы, затем каталоги с заголовком."""
        out, _ = run_lines(deep_shell(), "ls docs src/main.py empty")
        self.assertEqual(
            out, "src/main.py\n\ndocs:\nguide.txt  notes\n\nempty:\n")

    def test_missing_path(self):
        """Несуществующий путь — ошибка, остальные пути выводятся."""
        shell = deep_shell()
        out, err = run_lines(shell, "ls nope src")
        self.assertEqual(
            err, "ls: cannot access 'nope': No such file or directory\n")
        self.assertEqual(out, "src:\nmain.py\n")
        self.assertEqual(shell.status, EXIT_FAILURE)

    def test_invalid_option(self):
        """Неизвестная опция — ошибка."""
        _, err = run_lines(deep_shell(), "ls -z")
        self.assertEqual(err, "ls: invalid option -- 'z'\n")


class CdTest(unittest.TestCase):
    """Команда cd."""

    def test_relative_and_prompt(self):
        """Переход по относительному пути меняет приглашение."""
        shell = deep_shell()
        run_lines(shell, "cd docs/notes")
        self.assertEqual(shell.cwd, ["docs", "notes"])
        self.assertTrue(shell.prompt().endswith(":~/docs/notes$ "))

    def test_parent_absolute_and_home(self):
        """Переходы .., абсолютный путь и домой."""
        shell = deep_shell()
        run_lines(shell, "cd docs/notes/archive", "cd ../..")
        self.assertEqual(shell.cwd, ["docs"])
        run_lines(shell, "cd /src")
        self.assertEqual(shell.cwd, ["src"])
        run_lines(shell, "cd")
        self.assertEqual(shell.cwd, [])

    def test_previous_dir(self):
        """cd - возвращает в предыдущий каталог и выводит путь."""
        shell = deep_shell()
        out, _ = run_lines(shell, "cd docs", "cd /src", "cd -")
        self.assertEqual(shell.cwd, ["docs"])
        self.assertEqual(out, "~/docs\n")

    def test_ls_relative_to_cwd(self):
        """ls работает относительно текущего каталога."""
        out, _ = run_lines(deep_shell(), "cd docs", "ls")
        self.assertEqual(out, "guide.txt  notes\n")

    def test_errors(self):
        """Ошибки: нет пути, файл вместо каталога, лишние аргументы."""
        shell = deep_shell()
        _, err = run_lines(shell, "cd nope", "cd README.txt", "cd a b")
        self.assertEqual(err.splitlines(), [
            "cd: nope: No such file or directory",
            "cd: README.txt: Not a directory",
            "cd: too many arguments",
        ])
        self.assertEqual(shell.cwd, [])


if __name__ == "__main__":
    unittest.main()
