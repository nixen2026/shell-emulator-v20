# Эмулятор оболочки UNIX-подобной ОС (вариант 20)

Практическая работа по дисциплине «Конфигурационное управление».

## 1. Общее описание

Консольное приложение (CLI) на Python, имитирующее работу в командной
строке UNIX-подобной ОС. Реализован этап 1 — минимальный прототип (REPL):

* приглашение к вводу строится из реальных данных ОС —
  `username@hostname:~$`;
* простой парсер разделяет ввод на команду и аргументы по пробелам;
* команды `ls` и `cd` — заглушки, выводящие своё имя и аргументы;
* команда `exit` завершает работу эмулятора.

Используется только стандартная библиотека Python 3.8+.

## 2. Функции и настройки

| Команда       | Описание                                                    |
|---------------|-------------------------------------------------------------|
| `ls [арг...]` | Заглушка: выводит `ls: args=[...]`                          |
| `cd [арг...]` | Заглушка: выводит `cd: args=[...]`                          |
| `exit [код]`  | Выход с кодом; без аргумента — код последней команды        |

Обработка ошибок:

* неизвестная команда — `имя: command not found`, код 127;
* `exit abc` — `exit: abc: numeric argument required`;
* `exit 1 2` — `exit: too many arguments`;
* пустая строка игнорируется, `Ctrl+D` (EOF) завершает работу.

Структура проекта:

```
src/emulator/      исходный код
  __main__.py      точка входа (python -m emulator)
  shell.py         приглашение, выполнение команд, REPL
  parser.py        разбор строки на команду и аргументы
  commands.py      встроенные команды
  errors.py        исключения ShellError и ExitRequest
tests/             модульные тесты (unittest)
run.sh, run.bat    запуск эмулятора
test.sh, test.bat  запуск тестов
```

## 3. Сборка и запуск тестов

Сборка не требуется. Запуск эмулятора:

```bash
./run.sh          # Linux / macOS
run.bat           # Windows
```

Запуск тестов:

```bash
./test.sh         # Linux / macOS
test.bat          # Windows
```

## 4. Примеры использования

```
$ ./run.sh
nixen@Egorei:~$ ls -l /home
ls: args=['-l', '/home']
nixen@Egorei:~$ cd docs
cd: args=['docs']
nixen@Egorei:~$ foo bar
foo: command not found
nixen@Egorei:~$ exit abc
exit: abc: numeric argument required
nixen@Egorei:~$ exit 1 2
exit: too many arguments
nixen@Egorei:~$ exit 5
$ echo $?
5
```
