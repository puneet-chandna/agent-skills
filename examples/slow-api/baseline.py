"""Original baseline: duplicate serialization and repeated linear membership."""
from data import encode, payload


def render(rows, selected):
    value = payload(rows, selected)
    return encode(value), len(encode(value))
