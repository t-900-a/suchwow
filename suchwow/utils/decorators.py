from flask import session, redirect, url_for, flash
from functools import wraps
from suchwow.models import Profile, Moderator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "auth" not in session or not session["auth"]:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "auth" not in session or not session["auth"]:
            return redirect(url_for("auth.login"))
        m = Moderator.filter(username=session["auth"]["preferred_username"])
        if m:
            return f(*args, **kwargs)
        else:
            flash("You are not a moderator")
            return redirect(url_for("index"))
    return decorated_function

def profile_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        un = session["auth"]["preferred_username"]
        if not Profile.filter(username=un):
            url = "{}?redirect={}".format(
                url_for("profile.edit"),
                url_for("post.create")
            )
            return redirect(url)
        return f(*args, **kwargs)
    return decorated_function
