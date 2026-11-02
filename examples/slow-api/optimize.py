"""Mode 2: build a request-local membership set, including construction cost."""
import baseline


def render(rows, selected):
    return baseline.render(rows, set(selected))
