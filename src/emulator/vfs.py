"""Виртуальная файловая система (VFS), хранящаяся только в памяти.

Источник VFS — ZIP-архив. Файл архива может храниться как в двоичном
виде, так и в текстовом виде base64. Архив читается в память целиком
и никогда не распаковывается на диск и не изменяется.
"""

import base64
import binascii
import hashlib
import io
import os
import zipfile
import zlib

SEPARATOR = "/"
CURRENT_DIR = "."
PARENT_DIR = ".."
ARCHIVE_ERRORS = (zipfile.BadZipFile, zlib.error, NotImplementedError,
                  RuntimeError, ValueError, EOFError)


class VfsError(Exception):
    """Ошибка загрузки VFS или операции над ней."""


class VfsFile:
    """Файл VFS: имя и содержимое (байты) в памяти."""

    is_dir = False

    def __init__(self, name, data=b""):
        """Создать файл с именем ``name`` и содержимым ``data``."""
        self.name = name
        self.data = data

    @property
    def size(self):
        """Размер файла в байтах."""
        return len(self.data)


class VfsDir:
    """Каталог VFS: имя и словарь дочерних узлов по именам."""

    is_dir = True

    def __init__(self, name):
        """Создать пустой каталог с именем ``name``."""
        self.name = name
        self.children = {}

    @property
    def size(self):
        """Размер каталога — число элементов в нём."""
        return len(self.children)


class Vfs:
    """Загруженная VFS: имя, хеш данных и дерево каталогов."""

    def __init__(self, name=None, data=b""):
        """Создать VFS с именем ``name`` по данным ZIP-архива ``data``.

        Без имени создаётся пустая незагруженная VFS из одного корня.
        """
        self.name = name
        self.sha256 = hashlib.sha256(data).hexdigest()
        self.root = VfsDir("")

    @property
    def loaded(self):
        """Признак того, что VFS загружена из архива."""
        return self.name is not None

    def add_entry(self, name, data=None):
        """Добавить элемент архива: каталог (data is None) или файл."""
        parts = split_entry_name(name)
        if not parts:
            return
        parent = self.make_dirs(parts[:-1])
        existing = parent.children.get(parts[-1])
        if data is None:
            if existing is None:
                parent.children[parts[-1]] = VfsDir(parts[-1])
            elif not existing.is_dir:
                raise VfsError(f"vfs: invalid format: conflict at '{name}'")
            return
        if existing is not None:
            raise VfsError(f"vfs: invalid format: duplicate '{name}'")
        parent.children[parts[-1]] = VfsFile(parts[-1], data)

    def make_dirs(self, parts):
        """Вернуть каталог по списку имён, создавая недостающие."""
        node = self.root
        for part in parts:
            child = node.children.get(part)
            if child is None:
                child = node.children[part] = VfsDir(part)
            elif not child.is_dir:
                raise VfsError(
                    f"vfs: invalid format: '{part}' is not a directory")
            node = child
        return node


def split_entry_name(name):
    """Разбить имя элемента ZIP-архива на части пути.

    Пустые части и ``.`` пропускаются; ``..`` считается ошибкой формата,
    так как указывает за пределы корня VFS.
    """
    parts = [part for part in name.replace("\\", SEPARATOR).split(SEPARATOR)
             if part not in ("", CURRENT_DIR)]
    if PARENT_DIR in parts:
        raise VfsError(f"vfs: invalid format: bad entry name '{name}'")
    return parts


def read_source(path):
    """Прочитать файл-источник VFS с диска и вернуть его байты."""
    if os.path.isdir(path):
        raise VfsError(f"vfs: is a directory: {path}")
    try:
        with open(path, "rb") as file:
            return file.read()
    except FileNotFoundError:
        raise VfsError(f"vfs: file not found: {path}") from None
    except OSError as exc:
        raise VfsError(
            f"vfs: cannot read '{path}': {exc.strerror}") from None


def decode_source(raw):
    """Вернуть байты ZIP-архива: исходные или декодированные из base64."""
    if zipfile.is_zipfile(io.BytesIO(raw)):
        return raw
    try:
        data = base64.b64decode(raw)
    except (binascii.Error, ValueError):
        data = b""
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise VfsError(
            "vfs: invalid format: expected a ZIP archive or base64 ZIP")
    return data


def load_vfs(path):
    """Загрузить VFS из ZIP-архива (или base64 ZIP) по пути ``path``.

    Все данные остаются в памяти. При ошибке выбрасывается VfsError.
    """
    data = decode_source(read_source(path))
    vfs = Vfs(os.path.basename(path), data)
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for info in archive.infolist():
                content = None if info.is_dir() else archive.read(info)
                vfs.add_entry(info.filename, content)
    except ARCHIVE_ERRORS as exc:
        raise VfsError(f"vfs: invalid format: {exc}") from None
    return vfs
