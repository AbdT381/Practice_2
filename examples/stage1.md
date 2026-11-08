# Этап 1. Минимальный прототип с конфигурацией

## Цель
Создать минимальное CLI-приложение с конфигурацией в TOML и
продемонстрировать вывод всех настраиваемых параметров и обработку
ошибок для каждого из них.

## Конфигурационный файл

`config.toml`:

```toml
package_name = "org.apache.commons:commons-lang3"
repo_url     = "https://repo1.maven.org/maven2"
repo_mode    = "url"
output_image = "graph.png"
max_depth    = 2
```

## Успешный запуск

```bash
$ python -m src.main --config config.toml --stage 1
=== Этап 1: конфигурация ===
Конфигурация:
  package_name = org.apache.commons:commons-lang3
  repo_url     = https://repo1.maven.org/maven2
  repo_mode    = url
  output_image = graph.png
  max_depth    = 2
```

Все пять настраиваемых параметров выведены в формате `ключ = значение`.

## Обработка ошибок

Каждый параметр валидируется отдельно в `src/config.py`.

### package_name

| Вход | Сообщение |
|---|---|
| `""` | `package_name должен быть непустой строкой` |
| `"abc"` | `package_name должен иметь формат groupId:artifactId` |
| `"abc:"` | `package_name: groupId и artifactId не должны быть пустыми` |
| `":def"` | `package_name: groupId и artifactId не должны быть пустыми` |
| `123` | `package_name должен быть непустой строкой` |

### repo_mode

| Вход | Сообщение |
|---|---|
| `"zip"` | `repo_mode должен быть одним из ['file', 'url']` |
| `123` | `repo_mode должен быть одним из ['file', 'url']` |

### repo_url

| Вход | Сообщение |
|---|---|
| `"ftp://x"` (mode=url) | `repo_url должен начинаться с http:// или https://` |
| `"nope.txt"` (mode=file) | `Файл тестового графа не найден: nope.txt` |
| `""` | `repo_url должен быть непустой строкой` |

### output_image

| Вход | Сообщение |
|---|---|
| `"graph.jpg"` | `output_image должен иметь расширение .png` |
| `""` | `output_image должен иметь расширение .png` |

### max_depth

| Вход | Сообщение |
|---|---|
| `0` | `max_depth должен быть в диапазоне [1; 50]` |
| `51` | `max_depth должен быть в диапазоне [1; 50]` |
| `true` | `max_depth должен быть целым числом` |
| `"3"` | `max_depth должен быть целым числом` |

### Файл и TOML

| Ситуация | Сообщение |
|---|---|
| Нет файла | `Конфигурационный файл не найден: <path>` |
| Нет ключа | `Отсутствует обязательный параметр: <key>` |
| Битый TOML | `Некорректный TOML: <детали>` |

## Вывод
Этап 1 выполнен: CLI работает, конфигурация читается из TOML,
все параметры выводятся, каждый параметр защищён собственной
проверкой с понятным сообщением.
