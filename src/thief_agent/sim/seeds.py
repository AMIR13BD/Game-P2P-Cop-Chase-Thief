"""Deterministic seed sequences for reproducible batches."""


def seed_sequence(base: int, count: int) -> list[int]:
    return [base + i for i in range(count)]
