"""CLI-точка входа (этапы 1–3)."""
from __future__ import annotations

import argparse
import sys

from .config import Config, ConfigError, load_config, print_config
from .graph import DependencyGraph, GraphError
from .maven_parser import (
    MavenParseError,
    fetch_direct_dependencies,
    load_test_repository,
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Граф зависимостей Maven-пакетов (этапы 1–3)"
    )
    parser.add_argument(
        "--config", required=True, help="Путь к TOML-конфигурации"
    )
    parser.add_argument(
        "--stage",
        choices=["1", "2", "3"],
        default="3",
        help="Какой этап продемонстрировать (по умолчанию 3)",
    )
    return parser.parse_args()


def _build_graph_from_url(cfg: Config) -> DependencyGraph:
    """Этап 3: BFS по зависимостям с ограничением глубины."""
    graph = DependencyGraph()
    graph.add_edge(cfg.package_name, "")  ''' регистрируем корень '''
    graph = DependencyGraph()
    graph._edges.setdefault(cfg.package_name, [])  ''' noqa: SLF001 '''
    queue: list[tuple[str, int]] = [(cfg.package_name, 0)]
    seen: set[str] = set()
    while queue:
        artifact, depth = queue.pop(0)
        if artifact in seen or depth >= cfg.max_depth:
            continue
        seen.add(artifact)
        try:
            deps = fetch_direct_dependencies(artifact, cfg.repo_url)
        except MavenParseError as exc:
            print(f"⚠ Не удалось получить зависимости {artifact}: {exc}")
            continue
        for dep in deps:
            graph.add_edge(artifact, dep)
            queue.append((dep, depth + 1))
    return graph


def _build_graph_from_file(cfg: Config) -> DependencyGraph:
    mapping = load_test_repository(cfg.repo_url)
    graph = DependencyGraph()
    graph.build_from_mapping(mapping)
    return graph


def _print_stage1(cfg: Config) -> None:
    print("=== Этап 1: конфигурация ===")
    print_config(cfg)
    print()


def _print_stage2(cfg: Config) -> None:
    print("=== Этап 2: прямые зависимости ===")
    if cfg.repo_mode != "url":
        print("⚠ Этап 2 требует repo_mode = \"url\"")
        return
    try:
        deps = fetch_direct_dependencies(cfg.package_name, cfg.repo_url)
    except MavenParseError as exc:
        print(f"✗ {exc}")
        return
    print(f"Прямые зависимости {cfg.package_name}:")
    if not deps:
        print("  (нет)")
    for dep in deps:
        print(f"  - {dep}")
    print()


def _print_stage3(cfg: Config, graph: DependencyGraph) -> None:
    print("=== Этап 3: граф с транзитивностью ===")
    reachable = graph.dfs_depth_limited(cfg.package_name, cfg.max_depth)
    print(f"Достижимые узлы (max_depth = {cfg.max_depth}):")
    for node, depth in sorted(reachable.items(), key=lambda kv: (kv[1], kv[0])):
        print(f"  [{depth}] {node}")

    print(f"\nВсего рёбер: {len(graph.edges())}")
    for src, dst in graph.edges():
        print(f"  {src} -> {dst}")

    if graph.has_cycle():
        print("\n⚠ В графе обнаружены циклы:")
        for cyc in graph.find_cycles():
            print("  " + " -> ".join(cyc))
    else:
        print("\n✓ Циклов нет")
    print()


def main() -> int:
    args = _parse_args()
    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"✗ Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1

    ''' Этап 1 всегда: вывод конфигурации '''
    _print_stage1(cfg)

    ''' Этап 2 '''
    if args.stage in {"2", "3"}:
        _print_stage2(cfg)

    ''' Этап 3 '''
    if args.stage == "3":
        try:
            if cfg.repo_mode == "file":
                graph = _build_graph_from_file(cfg)
            else:
                graph = _build_graph_from_url(cfg)
        except (MavenParseError, GraphError, OSError) as exc:
            print(f"✗ Ошибка построения графа: {exc}", file=sys.stderr)
            return 2
        _print_stage3(cfg, graph)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
