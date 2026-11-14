import pytest

from src.config import (
    ConfigError,
    _validate_depth,
    _validate_mode,
    _validate_output_image,
    _validate_package_name,
    _validate_repo_url,
)


import pytest

from src.config import ConfigError, _validate_package_name


'''---------- режим url: groupId:artifactId ----------'''

def test_valid_package_name_url_mode() -> None:
    _validate_package_name("org.apache.commons:commons-lang3", "url")


@pytest.mark.parametrize(
    "name", ["", "abc", "abc:", ":def", 123, None]
)
def test_invalid_package_name_url_mode(name: object) -> None:
    with pytest.raises(ConfigError):
        _validate_package_name(name, "url")  ''' type: ignore[arg-type] '''


''' ---------- режим file: заглавные латинские буквы ---------- '''

@pytest.mark.parametrize("name", ["A", "B", "ABCDEF", "XYZ"])
def test_valid_package_name_file_mode(name: str) -> None:
    _validate_package_name(name, "file")


@pytest.mark.parametrize(
    "name",
    ["", "a", "Ab", "A1", "A:B", "A B", "АБВ", 123, None],
)
def test_invalid_package_name_file_mode(name: object) -> None:
    with pytest.raises(ConfigError):
        _validate_package_name(name, "file")  # type: ignore[arg-type]


'''---------- неизвестный режим ----------'''

def test_unknown_mode_rejected() -> None:
    with pytest.raises(ConfigError):
        _validate_package_name("A", "zip")


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
