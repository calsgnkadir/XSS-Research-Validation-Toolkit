# HTML-body escaping and template-parameter examples. The linter keeps these
# candidates below HIGH; this is neither runtime proof nor sanitizer validation.
from flask import Flask, request, render_template_string
from markupsafe import Markup
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
import html
import markupsafe
import bleach

app = Flask(__name__)
fapi = FastAPI()


# User input is a template parameter, never template source (SSTI boundary).
@app.get("/search")
def search():
    q = request.args.get("q", "")
    return render_template_string("<h1>Results for {{ q }}</h1>", q=q)


# markupsafe.escape same-line
@app.get("/user")
def user_page():
    name = request.args["name"]
    return Markup("Hello " + markupsafe.escape(name))


# FastAPI + bleach.clean
@fapi.get("/hi", response_class=HTMLResponse)
def hi(q: str = Query("")):
    return "<p>hi " + bleach.clean(q) + "</p>"


# Constant string - no attacker data at all
@app.get("/static")
def static():
    return "<h1>Static welcome</h1>"
