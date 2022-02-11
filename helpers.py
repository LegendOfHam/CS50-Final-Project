import os
import requests
import urllib.parse

from flask import redirect, flash, render_template, request, session
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            flash("Login required before proceeding!", "error")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function