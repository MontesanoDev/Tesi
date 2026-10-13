"""Bounded, serializable model data; reject invalid text instead of repairing facts."""

import json
import math


def checked_tree(value):
    stack, visited = [(value, 0)], 0
    while stack:
        item, depth = stack.pop()
        visited += 1
        if depth > 48 or visited > 100_000:
            raise ValueError("Struttura JSON oltre il limite di profondità/dimensione")
        if isinstance(item, str):
            try:
                item.encode("utf-8")
            except UnicodeError as exc:
                raise ValueError("Testo JSON con Unicode non valido") from exc
        elif isinstance(item, float) and not math.isfinite(item):
            raise ValueError("Numero JSON non finito")
        elif isinstance(item, dict):
            stack.extend((v, depth + 1) for pair in item.items() for v in pair)
        elif isinstance(item, list):
            stack.extend((v, depth + 1) for v in item)
    return value


def checked_json(raw, **kwargs):
    try:
        return checked_tree(json.loads(raw, **kwargs))
    except RecursionError as exc:
        raise ValueError("Struttura JSON troppo profonda") from exc
