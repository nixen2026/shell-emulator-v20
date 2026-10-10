# Эмулятор оболочки UNIX-подобной ОС (вариант 20)

Практическая работа по дисциплине «Конфигурационное управление».

## 1. Общее описание

Консольное приложение (CLI) на Python, имитирующее работу в командной
строке UNIX-подобной ОС. Используется только стандартная библиотека
Python 3.8+.

Реализованные этапы:

1. **REPL** — приглашение `username@hostname:~$` из реальных данных ОС,
   парсер команд по пробелам, заглушки `ls`, `cd`, команда `exit`.
2. **Конфигурация** — параметры командной строки (путь к VFS и к
   стартовому скрипту), стартовый скрипт с комментариями,
   служебная команда `conf-dump`, отладочный вывод параметров.
3. **VFS** — виртуальная файловая система из ZIP-архива (двоичного или
   в текстовом формате base64), хранится только в памяти; служебная
   команда `vfs-info`.

## 2. Функции и настройки

### Параметры командной строки

| Параметр        | Описание                                   |
|-----------------|--------------------------------------------|
| `--vfs PATH`    | путь к физическому расположению VFS        |
| `--script PATH` | путь к стартовому скрипту эмулятора        |
| `-h`, `--help`  | справка по параметрам                      |

При запуске все параметры выводятся в отладочном виде
(`[debug] ключ=значение`). Неизвестный параметр или параметр без
значения — ошибка argparse, код завершения 2.

### Команды

| Команда       | Описание                                                    |
|---------------|-------------------------------------------------------------|
| `ls [арг...]` | Заглушка: выводит `ls: args=[...]`                          |
| `cd [арг...]` | Заглушка: выводит `cd: args=[...]`                          |
| `exit [код]`  | Выход с кодом; без аргумента — код последней команды        |
| `conf-dump`   | Вывод параметров эмулятора в формате `ключ=значение`        |
| `vfs-info`    | Имя загруженной VFS и хеш SHA-256 её данных                 |

### Стартовый скрипт

* Текстовый файл (UTF-8), по одной команде в строке.
* Комментарии — как в Python: от `#` до конца строки
  (целая строка или конец строки с командой).
* При выполнении на экран выводится приглашение и сама команда, затем
  её вывод — имитируется диалог с пользователем.
* Об ошибке команды сообщается с номером строки:
  `путь:N: error: command exited with status S`; выполнение
  продолжается.
* `exit` в скрипте завершает эмулятор; иначе после скрипта
  запускается интерактивный режим.
* Если файл скрипта не читается — `script: cannot read ...`, код 1.

### Виртуальная файловая система (VFS)

* Источник VFS — ZIP-архив, путь задаётся параметром `--vfs`.
* Файл может быть двоичным ZIP или текстовым файлом с ZIP в base64
  (формат определяется автоматически).
* Архив целиком читается в память; на диск ничего не распаковывается,
  файл-источник не изменяется.
* `vfs-info` выводит имя файла VFS и SHA-256 данных ZIP-архива
  (для base64 — после декодирования, поэтому хеш совпадает).
* Ошибки загрузки (эмулятор завершается с кодом 1):
  `vfs: file not found: ...`, `vfs: is a directory: ...`,
  `vfs: invalid format: ...` (не ZIP, повреждённый архив,
  элемент с `..` в имени).
* Без `--vfs` используется пустая VFS, а `vfs-info` сообщает
  `vfs-info: VFS is not loaded`.

### Обработка ошибок

* неизвестная команда — `имя: command not found`, код 127;
* `exit abc` — `exit: abc: numeric argument required`;
* `exit 1 2`, `conf-dump x`, `vfs-info x` — `...: too many arguments`;
* пустая строка игнорируется, `Ctrl+D` (EOF) завершает работу.

### Структура проекта

```
src/emulator/      исходный код
  __main__.py      точка входа (python -m emulator)
  shell.py         приглашение, выполнение команд и скриптов, REPL
  parser.py        разбор строки: комментарии, команда, аргументы
  config.py        параметры командной строки
  vfs.py           VFS: загрузка ZIP в память, дерево каталогов
  commands.py      встроенные команды
  errors.py        исключения ShellError и ExitRequest
tests/             модульные тесты (unittest)
scripts/startup/   стартовые скрипты эмулятора
scripts/os/        скрипты ОС (.sh и .bat) для проверки эмулятора
scripts/make_vfs.py  генератор тестовых VFS в build/vfs
run.sh, run.bat    запуск эмулятора
test.sh, test.bat  запуск тестов
```

## 3. Сборка и запуск тестов

Сборка не требуется. Запуск эмулятора:

```bash
./run.sh [--vfs PATH] [--script PATH]
```

```bat
run.bat [--vfs PATH] [--script PATH]
```

Запуск модульных тестов:

```bash
./test.sh
```

```bat
test.bat
```

Тестовые VFS (архивы не хранятся в репозитории) создаются командой:

```bash
python scripts/make_vfs.py
```

В `build/vfs` появятся `minimal` (один файл), `several` (несколько
файлов), `deep` (3+ уровня вложенности, пустой каталог, двоичный файл)
в виде `.zip` и `.b64`, а также `broken.zip` неверного формата.

Скрипты ОС, проверяющие эмулятор (тестовые VFS создают сами):

| Linux / macOS                  | Windows                         |
|--------------------------------|---------------------------------|
| `scripts/os/test_params.sh`    | `scripts\os\test_params.bat`    |
| `scripts/os/test_startup.sh`   | `scripts\os\test_startup.bat`   |
| `scripts/os/test_vfs.sh`       | `scripts\os\test_vfs.bat`       |

## 4. Примеры использования

Интерактивный режим:

```
$ ./run.sh
[debug] vfs=<not set>
[debug] script=<not set>
nixen@Egorei:~$ ls -l /home
ls: args=['-l', '/home']
nixen@Egorei:~$ cd docs   # комментарий
cd: args=['docs']
nixen@Egorei:~$ foo bar
foo: command not found
nixen@Egorei:~$ exit abc
exit: abc: numeric argument required
nixen@Egorei:~$ exit 5
$ echo $?
5
```

Стартовый скрипт `scripts/startup/stage2.txt`:

```
$ ./run.sh --vfs my.zip --script scripts/startup/stage2.txt
[debug] vfs=my.zip
[debug] script=scripts/startup/stage2.txt
nixen@Egorei:~$ conf-dump
vfs=my.zip
script=scripts/startup/stage2.txt
nixen@Egorei:~$ ls -l /home   # комментарий в конце строки
ls: args=['-l', '/home']
nixen@Egorei:~$ cd docs
cd: args=['docs']
nixen@Egorei:~$ unknown-command arg
unknown-command: command not found
scripts/startup/stage2.txt:12: error: command exited with status 127
nixen@Egorei:~$ conf-dump extra
conf-dump: too many arguments
scripts/startup/stage2.txt:13: error: command exited with status 1
...
nixen@Egorei:~$ exit 0
```

Информация о VFS и ошибка формата:

```
$ ./run.sh --vfs build/vfs/deep.b64
[debug] vfs=build/vfs/deep.b64
[debug] script=<not set>
nixen@Egorei:~$ vfs-info
name: deep.b64
sha256: 3a078ed864f02c2fc5bd780b6713d2e187b1ce52721bfa19b8ff00a346c11a69
nixen@Egorei:~$ exit
$ ./run.sh --vfs build/vfs/broken.zip
[debug] vfs=build/vfs/broken.zip
[debug] script=<not set>
vfs: invalid format: expected a ZIP archive or base64 ZIP
```
