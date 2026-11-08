"""Загрузка и валидация TOML-конфигурации (этап 1)."""
from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

VALID_MODES = {"url", "file"}
MIN_DEPTH = 1
MAX_DEPTH = 50


class ConfigError(ValueError):
    """Ошибка конфигурации."""


@dataclass(frozen=True)
class Config:
    package_name: str
    repo_url: str
    repo_mode: str
    output_image: str
    max_depth: int


def _validate_package_name(name: object) -> None:
    if not isinstance(name, str) or not name:
        raise ConfigError("package_name должен быть непустой строкой")
    if ":" not in name:
        raise ConfigError(
            "package_name должен иметь формат groupId:artifactId"
        )
    group, artifact = name.split(":", maxsplit=1)
    if not group or not artifact:
        raise ConfigError(
            "package_name: groupId и artifactId не должны быть пустыми"
        )


def _validate_mode(mode: object) -> None:
    if mode not in VALID_MODES:
        raise ConfigError(
            f"repo_mode должен быть одним из {sorted(VALID_MODES)}"
        )


def _validate_repo_url(url: object, mode: str) -> None:
    if not isinstance(url, str) or not url:
        raise ConfigError("repo_url должен быть непустой строкой")
    if mode == "url":
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ConfigError(
                "repo_url должен начинаться с http:// или https://"
            )
    elif mode == "file":
        if not Path(url).exists():
            raise ConfigError(f"Файл тестового графа не найден: {url}")


def _validate_output_image(name: object) -> None:
    if not isinstance(name, str) or not name.endswith(".png"):
        raise ConfigError("output_image должен иметь расширение .png")


def _validate_depth(depth: object) -> None:
    if not isinstance(depth, int) or isinstance(depth, bool):
        raise ConfigError("max_depth должен быть целым числом")
    if not MIN_DEPTH <= depth <= MAX_DEPTH:
        raise ConfigError(
            f"max_depth должен быть в диапазоне [{MIN_DEPTH}; {MAX_DEPTH}]"
        )


def load_config(path: str | Path) -> Config:
    """Загрузить и провалидировать TOML-конфигурацию."""
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"Конфигурационный файл не найден: {path}")

    try:
        with path.open("rb") as f:
            raw = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Некорректный TOML: {exc}") from exc

    required = (
        "package_name", "repo_url", "repo_mode",
        "output_image", "max_depth",
    )
    for key in required:
        if key not in raw:
            raise ConfigError(f"Отсутствует обязательный параметр: {key}")

    cfg = Config(
        package_name=raw["package_name"],
        repo_url=raw["repo_url"],
        repo_mode=raw["repo_mode"],
        output_image=raw["output_image"],
        max_depth=raw["max_depth"],
    )

    _validate_package_name(cfg.package_name)
    _validate_mode(cfg.repo_mode)
    _validate_repo_url(cfg.repo_url, cfg.repo_mode)
    _validate_output_image(cfg.output_image)
    _validate_depth(cfg.max_depth)

    return cfg


def print_config(cfg: Config) -> None:
    """Вывести все настраиваемые параметры в формате ключ-значение."""
    print("Конфигурация:")
    print(f"  package_name = {cfg.package_name}")
    print(f"  repo_url     = {cfg.repo_url}")
    print(f"  repo_mode    = {cfg.repo_mode}")
    print(f"  output_image = {cfg.output_image}")
    print(f"  max_depth    = {cfg.max_depth}")
