"""Граф зависимостей и DFS без рекурсии (этап 3)."""
from __future__ import annotations

from collections import defaultdict


class GraphError(RuntimeError):
    """Ошибка работы с графом."""


class DependencyGraph:
    """Ориентированный граф: A -> B означает, что A зависит от B."""

    def __init__(self) -> None:
        self._edges: dict[str, list[str]] = defaultdict(list)
        self._reverse: dict[str, list[str]] = defaultdict(list)

    def add_edge(self, src: str, dst: str) -> None:
        if dst not in self._edges[src]:
            self._edges[src].append(dst)
            self._reverse[dst].append(src)

    def nodes(self) -> list[str]:
        return sorted(self._edges.keys())

    def edges(self) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        for src in self.nodes():
            for dst in self._edges[src]:
                result.append((src, dst))
        return result

    def build_from_mapping(self, mapping: dict[str, list[str]]) -> None:
        for node, deps in mapping.items():
            self._edges.setdefault(node, [])
            for dep in deps:
                self.add_edge(node, dep)

    '''
    Этап 3: DFS без рекурсии, ограничение глубины, циклы
    '''
    def dfs_depth_limited(
        self, start: str, max_depth: int
    ) -> dict[str, int]:
        """DFS без рекурсии. Возвращает {узел: минимальная глубина}.

        Циклы обрабатываются: узел пересматривается только если
        он достижим на строго меньшей глубине, чем посещён ранее.
        """
        if start not in self._edges:
            raise GraphError(f"Пакет не найден в графе: {start}")
        if max_depth < 1:
            raise GraphError("max_depth должен быть >= 1")

        visited: dict[str, int] = {start: 0}
        stack: list[tuple[str, int]] = [(start, 0)]
        while stack:
            node, depth = stack.pop()
            if depth >= max_depth:
                continue
            for neighbor in self._edges.get(node, []):
                next_depth = depth + 1
                if (
                    neighbor not in visited
                    or next_depth < visited[neighbor]
                ):
                    visited[neighbor] = next_depth
                    stack.append((neighbor, next_depth))
        return visited

    def has_cycle(self) -> bool:
        """Проверка наличия циклов. DFS без рекурсии, цветовая схема."""
        white, gray, black = 0, 1, 2
        color: dict[str, int] = defaultdict(int)
        for start in self._edges:
            if color[start] != white:
                continue
            stack: list[tuple[str, int]] = [(start, 0)]
            color[start] = gray
            while stack:
                node, idx = stack[-1]
                neighbors = self._edges.get(node, [])
                if idx < len(neighbors):
                    stack[-1] = (node, idx + 1)
                    nxt = neighbors[idx]
                    if color[nxt] == gray:
                        return True
                    if color[nxt] == white:
                        color[nxt] = gray
                        stack.append((nxt, 0))
                else:
                    color[node] = black
                    stack.pop()
        return False

    def find_cycles(self) -> list[list[str]]:
        """Найти все элементарные циклы (для отчёта на этапе 3)."""
        cycles: list[list[str]] = []
        nodes = self.nodes()
        for start in nodes:
            stack: list[tuple[str, list[str]]] = [(start, [start])]
            while stack:
                node, path = stack.pop()
                for nxt in self._edges.get(node, []):
                    if nxt == start and len(path) > 1:
                        cycles.append(path + [start])
                    elif nxt not in path:
                        stack.append((nxt, path + [nxt]))
        ''' нормализуем: оставляем уникальные циклы '''
        unique: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()
        for cyc in cycles:
            body = cyc[:-1]
            ''' каноническая форма — минимальный поворот '''
            rotations = [
                tuple(body[i:] + body[:i]) for i in range(len(body))
            ]
            key = min(rotations)
            if key not in seen:
                seen.add(key)
                unique.append(list(key) + [key[0]])
        return unique
