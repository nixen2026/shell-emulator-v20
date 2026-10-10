"""Тесты команд rm и mv, изменяющих VFS только в памяти."""

import os
import tempfile
import unittest

from emulator.errors import EXIT_FAILURE, EXIT_SUCCESS
from emulator.vfs import load_vfs
from helpers import DEEP_LAYOUT, make_shell, make_vfs, make_zip, run_lines


def deep_shell():
    """Создать эмулятор с тестовой VFS из нескольких уровней."""
    return make_shell(vfs=make_vfs())


def exists(shell, path):
    """Проверить существование пути в VFS эмулятора."""
    return shell.vfs.find(shell.resolve(path)) is not None


class RmTest(unittest.TestCase):
    """Команда rm."""

    def test_remove_files(self):
        """Удаление одного и нескольких файлов."""
        shell = deep_shell()
        run_lines(shell, "rm README.txt", "rm docs/guide.txt src/main.py")
        for path in ("README.txt", "docs/guide.txt", "src/main.py"):
            self.assertFalse(exists(shell, path))
        self.assertEqual(shell.status, EXIT_SUCCESS)

    def test_directory_requires_recursive(self):
        """Каталог без -r не удаляется, с -r удаляется целиком."""
        shell = deep_shell()
        _, err = run_lines(shell, "rm docs")
        self.assertEqual(err, "rm: cannot remove 'docs': Is a directory\n")
        self.assertTrue(exists(shell, "docs/notes/todo.txt"))
        run_lines(shell, "rm -r docs")
        self.assertFalse(exists(shell, "docs"))

    def test_missing_and_force(self):
        """Несуществующий путь — ошибка; с -f ошибки нет."""
        shell = deep_shell()
        _, err = run_lines(shell, "rm nope README.txt")
        self.assertEqual(
            err, "rm: cannot remove 'nope': No such file or directory\n")
        self.assertFalse(exists(shell, "README.txt"))
        self.assertEqual(shell.status, EXIT_FAILURE)
        _, err = run_lines(shell, "rm -f nope")
        self.assertEqual(shell.status, EXIT_SUCCESS)

    def test_protected_paths(self):
        """Нельзя удалить корень и каталог, содержащий текущий."""
        shell = deep_shell()
        _, err = run_lines(shell, "rm -r /", "cd docs/notes", "rm -r ..")
        self.assertEqual(err.splitlines(), [
            "rm: refusing to remove root directory '/'",
            "rm: cannot remove '..': current directory is inside it",
        ])
        self.assertTrue(exists(shell, "/docs"))

    def test_usage_errors(self):
        """Нет операндов и неизвестная опция."""
        _, err = run_lines(deep_shell(), "rm", "rm -x a")
        self.assertEqual(err.splitlines(), [
            "rm: missing operand", "rm: invalid option -- 'x'"])

    def test_source_file_not_modified(self):
        """Изменения VFS не затрагивают файл-источник на диске."""
        data = make_zip(DEEP_LAYOUT)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "deep.zip")
            with open(path, "wb") as file:
                file.write(data)
            shell = make_shell(vfs=load_vfs(path))
            run_lines(shell, "rm -r docs", "mv src code")
            with open(path, "rb") as file:
                self.assertEqual(file.read(), data)
        self.assertFalse(exists(shell, "docs"))


class MvTest(unittest.TestCase):
    """Команда mv."""

    def test_rename_file(self):
        """Переименование файла с сохранением содержимого."""
        shell = deep_shell()
        run_lines(shell, "mv README.txt INFO.txt")
        self.assertFalse(exists(shell, "README.txt"))
        node = shell.lookup("INFO.txt")
        self.assertEqual((node.name, node.data), ("INFO.txt", b"readme\n"))

    def test_move_into_directory(self):
        """Перемещение нескольких элементов в каталог."""
        shell = deep_shell()
        out, _ = run_lines(shell, "mv README.txt src docs/notes", "ls ~")
        self.assertTrue(exists(shell, "docs/notes/README.txt"))
        self.assertTrue(exists(shell, "docs/notes/src/main.py"))
        self.assertEqual(out, "docs  empty\n")

    def test_rename_directory_updates_cwd(self):
        """Переименование каталога, содержащего текущий, меняет cwd."""
        shell = deep_shell()
        run_lines(shell, "cd docs/notes", "mv /docs /manuals")
        self.assertEqual(shell.cwd, ["manuals", "notes"])
        self.assertTrue(shell.prompt().endswith(":~/manuals/notes$ "))

    def test_overwrite_file(self):
        """Существующий файл назначения заменяется."""
        shell = deep_shell()
        run_lines(shell, "mv docs/guide.txt README.txt")
        self.assertEqual(shell.lookup("README.txt").data, b"guide\n")
        self.assertFalse(exists(shell, "docs/guide.txt"))

    def test_move_errors(self):
        """Ошибки перемещения отдельных источников."""
        shell = deep_shell()
        _, err = run_lines(
            shell, "mv nope empty", "mv docs docs/notes",
            "mv README.txt README.txt", "mv src/main.py no/such",
            "mv README.txt docs/notes/todo.txt/x")
        self.assertEqual(err.splitlines(), [
            "mv: cannot stat 'nope': No such file or directory",
            "mv: cannot move 'docs' to a subdirectory of itself, "
            "'docs/notes/docs'",
            "mv: 'README.txt' and 'README.txt' are the same file",
            "mv: cannot move 'src/main.py' to 'no/such': "
            "No such file or directory",
            "mv: cannot move 'README.txt' to 'docs/notes/todo.txt/x': "
            "No such file or directory",
        ])

    def test_overwrite_errors(self):
        """Нельзя заменить каталог или заменить файл каталогом."""
        shell = deep_shell()
        _, err = run_lines(shell, "mv empty notes", "mv notes docs",
                           "mv notes README.txt")
        self.assertEqual(err.splitlines(), [
            "mv: cannot overwrite directory 'docs/notes'",
            "mv: cannot overwrite non-directory 'README.txt' "
            "with directory 'notes'",
        ])
        self.assertTrue(exists(shell, "notes"))

    def test_usage_errors(self):
        """Ошибки операндов mv."""
        _, err = run_lines(deep_shell(), "mv", "mv a",
                           "mv src/main.py docs/guide.txt README.txt",
                           "mv README.txt src new_dir")
        self.assertEqual(err.splitlines(), [
            "mv: missing file operand",
            "mv: missing destination file operand after 'a'",
            "mv: target 'README.txt' is not a directory",
            "mv: target 'new_dir' is not a directory",
        ])


if __name__ == "__main__":
    unittest.main()
