 Этап 2. Сбор данных: прямые зависимости Maven

 Цель
Получить прямые зависимости Java/Maven-пакета по URL репозитория
**без** использования менеджеров пакетов и сторонних библиотек,
вывести их на экран.

 Принцип работы

1. Запрос `maven-metadata.xml`:
   ```
   <repo_url>/<group/path>/<artifact>/maven-metadata.xml
   ```
   Из него берётся `<versioning><release>` (fallback — `<latest>`).

2. Скачивание POM-файла:
   ```
   <repo_url>/<group/path>/<artifact>/<version>/<artifact>-<version>.pom
   ```

3. Разбор `<dependencies>` через `xml.etree.ElementTree` (стандартная
   библиотека Python), пространство имён Maven:
   `http://maven.apache.org/POM/4.0.0`.

4. Каждая зависимость возвращается в формате `groupId:artifactId`.

 Запуск

```bash
$ python -m src.main --config config.toml --stage 2
=== Этап 1: конфигурация ===
Конфигурация:
  package_name = org.apache.commons:commons-lang3
  repo_url     = https://repo1.maven.org/maven2
  repo_mode    = url
  output_image = graph.png
  max_depth    = 2

=== Этап 2: прямые зависимости ===
Прямые зависимости org.apache.commons:commons-lang3:
  - org.apache.commons:commons-parent
  - junit:junit
  - org.apache.maven.plugins:maven-javadoc-plugin
  - ...
```

> Точный список зависит от версии `commons-lang3`, актуальной в
> `maven-metadata.xml` на момент запуска. Набор прямых зависимостей
> фиксируется в выводе, чтобы проверяющий мог сверить с
> `mvn dependency:list`.

 Обработка ошибок

| Ситуация | Сообщение |
|---|---|
| `repo_mode = "file"` | `⚠ Этап 2 требует repo_mode = "url"` |
| Нет `maven-metadata.xml` | `Не удалось загрузить <url>: <детали>` |
| Нет `<release>`/`<latest>` | `Не найдена версия для <artifact>` |
| Некорректный POM | `Некорректный XML в <url>: <детали>` |
| Нет `<dependencies>` | пустой список, выводится `(нет)` |

 Ограничения (соблюдены)

- **Не используется** `mvn`, `mvn dependency:list`, Maven Resolver,
  `requests`, `lxml`, `packaging` и т.п.
- Разрешены только модули стандартной библиотеки: `urllib.request`,
  `xml.etree.ElementTree`, `pathlib`.

 Вывод
Этап 2 выполнен: прямые зависимости извлекаются вручную, выводятся
на экран, ошибки загрузки/разбора обрабатываются.
