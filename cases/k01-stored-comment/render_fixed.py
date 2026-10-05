"""K01 fixture v1.0: HTML text-context output encoding."""
import html


def render(comment):
    value = html.escape(comment, quote=True)
    return '<!doctype html><meta charset="utf-8"><h1>Comments</h1><article id="comment">' + value + '</article>'
