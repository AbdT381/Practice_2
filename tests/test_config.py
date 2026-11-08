import pytest

from src.config import (
    ConfigError,
    _validate_depth,
    _validate_mode,
    _validate_output_image,
    _validate_package_name,
    _validate_repo_url,
)


def test_valid_package_name() -> None:
    _validate_package_name("org.apache.commons:commons-lang3")


@pytest.mark.parametrize("name", ["", "abc", "abc:", ":def", 123, None])
def test_invalid_package_name(name: object) -> None:
    with pytest.raises(ConfigError):
        _validate_package_name(name)  # type: ignore[arg-type]


def test_depth_bounds() -> None:
    _validate_depth(1)
    _validate_depth(50)
    with pytest.raises(ConfigError):
        _validate_depth(0)
    with pytest.raises(ConfigError):
        _validate_depth(51)
    with pytest.raises(ConfigError):
        _validate_depth(True)


def test_mode_and_url() -> None:
    with pytest.raises(ConfigError):
        _validate_mode("zip")
    with pytest.raises(ConfigError):
        _validate_repo_url("ftp://x", "url")
    with pytest.raises(ConfigError):
        _validate_repo_url("nope.txt", "file")


def test_output_image() -> None:
    _validate_output_image("graph.png")
    with pytest.raises(ConfigError):
        _validate_output_image("graph.jpg")
