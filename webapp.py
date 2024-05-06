#!/usr/bin/env python3
import functools
import secrets
from datetime import datetime, timedelta
from typing import Iterable

from flask import (Flask, render_template, request, redirect, url_for, session,
                   make_response)
from passlib.hash import pbkdf2_sha256

from chores import Chore, LastCompletedDb, parse_chores

db = LastCompletedDb("last_completed.json")

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=1000000)
app.secret_key = secrets.token_hex()

USERNAME = "joe"

with open(".passwd") as f:
    # Generated with
    # from passlib.hash import pbkdf2_sha256
    # pbkdf2_sha256.using(rounds=8000, salt_size=10).hash(password)
    PASSWORD_HASH = f.read().strip()


def get_chores() -> Iterable[Chore]:
    """
    Parse the chore definition CSV file and return a list of chores, sorted by
    next-due date (soonest first)
    """
    with open("chores.csv") as f:
        return sorted(list(parse_chores(db, f)))

def requires_login(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        # Already logged in
        if "you_are_joe" in session:
            return func(*args, **kwargs)
        # Check for password and verify
        auth = request.authorization
        if auth is not None:
            username = auth.get("username") or ""
            password = auth.get("password") or ""
            if (username == USERNAME
                    and pbkdf2_sha256.verify(password, PASSWORD_HASH)):
                session["you_are_joe"] = True
                session.permanent = True
                return func(*args, **kwargs)
        # Request authentication
        return make_response((
            "are you joe?",
            401, {"WWW-Authenticate": "Basic realm=chores charset=UTF-8"}
        ))
    return inner

@app.route("/", methods=("GET",))
@requires_login
def home():
    chore_data = []
    today_at_midnight = datetime.now().date()
    for chore in get_chores():
        chore_data.append({
            "name": chore.name,
            "frequency": str(chore.frequency),
            "due_in_days": (chore.next_due - today_at_midnight).days
        })
    return render_template("index.html", chores=chore_data)

@app.route("/complete", methods=("POST",))
@requires_login
def complete():
    if "completed" in request.form:
        for name in request.form.getlist("completed"):
            db.complete(name)
        db.save()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
