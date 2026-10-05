"""K01 fixture v1.0: deliberately unsafe HTML text-context rendering."""
import html


def render(comment):
    value = comment
    return '<!doctype html><meta charset="utf-8"><h1>Comments</h1><article id="comment">' + value + '</article>'
