"""Mode 1: serialize the unchanged response once."""
from data import encode, payload


def render(rows, selected):
    body = encode(payload(rows, selected))
    return body, len(body)
