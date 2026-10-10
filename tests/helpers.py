"""Вспомогательные средства для тестов эмулятора."""

import io
import zipfile

from emulator.shell import Shell
from emulator.vfs import Vfs

DEEP_LAYOUT = {
    "README.txt": b"readme\n",
    "docs/guide.txt": b"guide\n",
    "docs/notes/todo.txt": b"todo\n",
    "docs/notes/archive/old.txt": b"old\n",
    "src/main.py": b"print(1)\n",
    "empty/": None,
}


def make_zip(layout):
    """Вернуть байты ZIP-архива; значение None означает каталог."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in layout.items():
            archive.writestr(name, data if data is not None else b"")
    return buffer.getvalue()


def make_vfs(layout=None, name="test.zip"):
    """Построить VFS в памяти по структуре ``layout``."""
    vfs = Vfs(name, make_zip(layout or DEEP_LAYOUT))
    for entry, data in (layout or DEEP_LAYOUT).items():
        vfs.add_entry(entry, data)
    return vfs


def make_shell(**kwargs):
    """Создать эмулятор, пишущий вывод и ошибки в буферы StringIO."""
    return Shell(out=io.StringIO(), err=io.StringIO(), **kwargs)


def run_lines(shell, *lines):
    """Выполнить строки и вернуть накопленные (вывод, ошибки)."""
    for line in lines:
        shell.execute(line)
    return shell.out.getvalue(), shell.err.getvalue()
