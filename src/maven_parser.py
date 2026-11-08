"""Получение зависимостей Maven без сторонних библиотек (этапы 2–3)."""
from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

MAVEN_NS = "{http://maven.apache.org/POM/4.0.0}"
TIMEOUT_SECONDS = 30
EXPECTED_FIELDS_IN_TEST_LINE = 1


class MavenParseError(RuntimeError):
    """Ошибка получения или разбора pom.xml / тестового графа."""


def _artifact_to_path(artifact: str) -> str:
    """org.apache.commons:commons-lang3 -> org/apache/commons/commons-lang3"""
    group, artifact_id = artifact.split(":", maxsplit=1)
    return group.replace(".", "/") + "/" + artifact_id


def _pom_url(repo_url: str, artifact: str, version: str) -> str:
    base = repo_url.rstrip("/")
    group, artifact_id = artifact.split(":", maxsplit=1)
    path = _artifact_to_path(artifact)
    return f"{base}/{path}/{version}/{artifact_id}-{version}.pom"


def _fetch_xml(url: str) -> ET.Element:
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as resp:
            data = resp.read()
    except Exception as exc:  # noqa: BLE001
        raise MavenParseError(f"Не удалось загрузить {url}: {exc}") from exc
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise MavenParseError(f"Некорректный XML в {url}: {exc}") from exc


def _resolve_version(root: ET.Element) -> str:
    version = root.findtext(f"{MAVEN_NS}version")
    if not version:
        parent = root.find(f"{MAVEN_NS}parent")
        if parent is not None:
            version = parent.findtext(f"{MAVEN_NS}version")
    if not version:
        raise MavenParseError("Не удалось определить версию пакета")
    return version


def _extract_dependencies(root: ET.Element) -> list[str]:
    deps = root.find(f"{MAVEN_NS}dependencies")
    if deps is None:
        return []
    result: list[str] = []
    for dep in deps.findall(f"{MAVEN_NS}dependency"):
        group = dep.findtext(f"{MAVEN_NS}groupId")
        artifact = dep.findtext(f"{MAVEN_NS}artifactId")
        if group and artifact:
            result.append(f"{group}:{artifact}")
    return result


def _latest_version(repo_url: str, artifact: str) -> str:
    meta_url = (
        f"{repo_url.rstrip('/')}/{_artifact_to_path(artifact)}"
        "/maven-metadata.xml"
    )
    meta = _fetch_xml(meta_url)
    version = (
        meta.findtext(f"{MAVEN_NS}versioning/{MAVEN_NS}release")
        or meta.findtext(f"{MAVEN_NS}versioning/{MAVEN_NS}latest")
    )
    if not version:
        raise MavenParseError(f"Не найдена версия для {artifact}")
    return version


def fetch_direct_dependencies(artifact: str, repo_url: str) -> list[str]:
    """Прямые зависимости пакета (этап 2)."""
    version = _latest_version(repo_url, artifact)
    pom = _fetch_xml(_pom_url(repo_url, artifact, version))
    return _extract_dependencies(pom)


def load_test_repository(path: str | Path) -> dict[str, list[str]]:
    """Загрузить тестовый граф (пакеты — большие латинские буквы)."""
    path = Path(path)
    graph: dict[str, list[str]] = {}
    for lineno, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise MavenParseError(
                f"Строка {lineno}: ожидается формат 'NAME: deps'"
            )
        node, _, deps = line.partition(":")
        node = node.strip()
        if not node.isupper() or not node.isalpha():
            raise MavenParseError(
                f"Строка {lineno}: имя пакета должно состоять "
                "из заглавных латинских букв"
            )
        fields = deps.split()
        if len(fields) < 0:  # защитная ветка, недостижима
            raise MavenParseError("Некорректная строка")
        graph[node] = fields
    if not graph:
        raise MavenParseError(f"Тестовый граф пуст: {path}")
    return graph
