"""Сгенерировать тестовые VFS (ZIP и base64 ZIP) в каталоге build/vfs.

Архивы не хранятся в репозитории, поэтому создаются этим скриптом:

* ``minimal`` — один файл;
* ``several`` — несколько файлов и каталог;
* ``deep`` — не менее трёх уровней вложенности, пустой каталог и
  двоичный файл;
* ``broken.zip`` — файл неверного формата для проверки ошибок.

Запуск: ``python scripts/make_vfs.py [каталог]``.
"""

import base64
import io
import os
import sys
import zipfile

FIXED_DATE = (2026, 1, 1, 0, 0, 0)
BINARY_DATA = bytes(range(256))

LAYOUTS = {
    "minimal": {
        "hello.txt": b"Hello, VFS!\n",
    },
    "several": {
        "readme.txt": b"Several files VFS\n",
        "notes.txt": b"note 1\nnote 2\n",
        "todo.txt": b"- write tests\n",
        "data/": None,
        "data/values.csv": b"a,b\n1,2\n",
    },
    "deep": {
        "README.txt": b"Deep VFS: three and more levels\n",
        "docs/guide.txt": b"How to use the emulator\n",
        "docs/notes/todo.txt": b"- stage 4\n- stage 5\n",
        "docs/notes/archive/2025/report.txt": b"Annual report\n",
        "src/main.py": b"print('hello')\n",
        "src/lib/utils.py": b"VALUE = 42\n",
        "images/logo.bin": BINARY_DATA,
        "empty/": None,
    },
}


def build_zip(layout):
    """Вернуть байты ZIP-архива с заданной структурой файлов.

    Дата элементов фиксирована, чтобы хеш архива был воспроизводим.
    """
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in layout.items():
            info = zipfile.ZipInfo(name, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data if data is not None else b"")
    return buffer.getvalue()


def write_file(path, data):
    """Записать байты в файл и вывести его путь."""
    with open(path, "wb") as file:
        file.write(data)
    print(f"created {path}")


def main(argv):
    """Создать все тестовые VFS в каталоге из ``argv`` или build/vfs."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = argv[0] if argv else os.path.join(root, "build", "vfs")
    os.makedirs(out_dir, exist_ok=True)
    for name, layout in LAYOUTS.items():
        data = build_zip(layout)
        write_file(os.path.join(out_dir, f"{name}.zip"), data)
        write_file(os.path.join(out_dir, f"{name}.b64"),
                   base64.encodebytes(data))
    write_file(os.path.join(out_dir, "broken.zip"), b"this is not a zip\n")


if __name__ == "__main__":
    main(sys.argv[1:])
