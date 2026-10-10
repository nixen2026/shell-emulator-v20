"""Тесты загрузки VFS из ZIP-архива и команды vfs-info."""

import base64
import hashlib
import os
import tempfile
import unittest

from emulator.vfs import VfsError, load_vfs
from helpers import DEEP_LAYOUT, make_shell, make_vfs, make_zip, run_lines


class LoadVfsTest(unittest.TestCase):
    """Загрузка VFS с диска."""

    def setUp(self):
        """Создать временный каталог для файлов VFS."""
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def write(self, name, data):
        """Записать файл во временный каталог и вернуть путь."""
        path = os.path.join(self.tmp.name, name)
        with open(path, "wb") as file:
            file.write(data)
        return path

    def test_load_zip(self):
        """Дерево каталогов строится по элементам архива."""
        data = make_zip(DEEP_LAYOUT)
        vfs = load_vfs(self.write("deep.zip", data))
        self.assertEqual(vfs.name, "deep.zip")
        self.assertEqual(vfs.sha256, hashlib.sha256(data).hexdigest())
        notes = vfs.root.children["docs"].children["notes"]
        self.assertTrue(notes.children["archive"].is_dir)
        self.assertEqual(notes.children["todo.txt"].data, b"todo\n")
        self.assertTrue(vfs.root.children["empty"].is_dir)

    def test_load_base64(self):
        """ZIP в формате base64 загружается так же, как двоичный."""
        data = make_zip({"a.txt": b"\x00\xff"})
        vfs = load_vfs(self.write("a.b64", base64.encodebytes(data)))
        self.assertEqual(vfs.root.children["a.txt"].data, b"\x00\xff")
        self.assertEqual(vfs.sha256, hashlib.sha256(data).hexdigest())

    def test_file_not_found(self):
        """Отсутствующий файл — ошибка «file not found»."""
        with self.assertRaisesRegex(VfsError, "file not found"):
            load_vfs(os.path.join(self.tmp.name, "none.zip"))

    def test_invalid_format(self):
        """Файл не в формате ZIP — ошибка «invalid format»."""
        with self.assertRaisesRegex(VfsError, "invalid format"):
            load_vfs(self.write("bad.zip", b"not a zip at all"))

    def test_directory_path(self):
        """Каталог вместо файла — ошибка чтения."""
        with self.assertRaises(VfsError):
            load_vfs(self.tmp.name)

    def test_parent_dir_entry(self):
        """Элемент архива с '..' считается ошибкой формата."""
        path = self.write("evil.zip", make_zip({"../x.txt": b"x"}))
        with self.assertRaisesRegex(VfsError, "bad entry name"):
            load_vfs(path)

    def test_source_not_modified(self):
        """Загрузка VFS не изменяет файл-источник."""
        data = make_zip(DEEP_LAYOUT)
        path = self.write("deep.zip", data)
        load_vfs(path)
        with open(path, "rb") as file:
            self.assertEqual(file.read(), data)


class VfsInfoTest(unittest.TestCase):
    """Служебная команда vfs-info."""

    def test_info(self):
        """vfs-info выводит имя VFS и SHA-256."""
        vfs = make_vfs(name="deep.zip")
        out, _ = run_lines(make_shell(vfs=vfs), "vfs-info")
        self.assertEqual(
            out, f"name: deep.zip\nsha256: {vfs.sha256}\n")

    def test_not_loaded(self):
        """Без VFS vfs-info сообщает об ошибке."""
        _, err = run_lines(make_shell(), "vfs-info")
        self.assertEqual(err, "vfs-info: VFS is not loaded\n")

    def test_extra_args(self):
        """vfs-info не принимает аргументов."""
        _, err = run_lines(make_shell(vfs=make_vfs()), "vfs-info x")
        self.assertEqual(err, "vfs-info: too many arguments\n")


if __name__ == "__main__":
    unittest.main()
