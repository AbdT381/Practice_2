import pytest

from src.graph import DependencyGraph, GraphError
from src.maven_parser import load_test_repository


def _build(path: str) -> DependencyGraph:
    g = DependencyGraph()
    g.build_from_mapping(load_test_repository(path))
    return g


def test_dfs_depth_limit() -> None:
    g = _build("tests/fixtures/deep_graph.txt")
    assert g.dfs_depth_limited("A", max_depth=2) == {"A": 0, "B": 1, "C": 2}
    assert g.dfs_depth_limited("A", max_depth=3) == {
        "A": 0, "B": 1, "C": 2, "D": 3,
    }


def test_dfs_unknown_node() -> None:
    g = _build("tests/fixtures/simple_graph.txt")
    with pytest.raises(GraphError):
        g.dfs_depth_limited("Z", max_depth=3)


def test_dfs_bad_depth() -> None:
    g = _build("tests/fixtures/simple_graph.txt")
    with pytest.raises(GraphError):
        g.dfs_depth_limited("A", max_depth=0)


def test_cycle_detection_true() -> None:
    g = _build("tests/fixtures/cyclic_graph.txt")
    assert g.has_cycle() is True


def test_cycle_detection_false() -> None:
    g = _build("tests/fixtures/deep_graph.txt")
    assert g.has_cycle() is False


def test_cycles_content() -> None:
    g = _build("tests/fixtures/simple_graph.txt")
    cycles = g.find_cycles()
    '''Ожидаем цикл A -> C -> E -> A (в каноническом виде начинается с A) '''
    assert any(set(c) >= {"A", "C", "E"} for c in cycles)


def test_cycle_does_not_hang() -> None:
    """DFS на циклическом графе должен корректно завершаться."""
    g = _build("tests/fixtures/cyclic_graph.txt")
    reachable = g.dfs_depth_limited("A", max_depth=10)
    assert set(reachable) >= {"A", "B", "C"}
