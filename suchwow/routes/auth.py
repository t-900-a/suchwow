import requests
from uuid import uuid4
from flask import session, redirect, url_for, request, Blueprint
from suchwow import config


bp = Blueprint("auth", "auth")

@bp.route("/login")
def login():
    state = uuid4().hex
    session["auth_state"] = state
    url = f"{config.OIDC_URL}/auth?" \
          f"client_id={config.OIDC_CLIENT_ID}&" \
          f"redirect_uri={config.OIDC_REDIRECT_URL}&" \
          f"response_type=code&" \
          f"state={state}"

    return redirect(url)

@bp.route("/logout")
def logout():
    session["auth"] = None
    return redirect(url_for("index"))

@bp.route("/auth/")
def auth():
    # todo - clean up assertions
    assert "state" in request.args
    assert "session_state" in request.args
    assert "code" in request.args

    # verify state
    if not session.get("auth_state"):
        return "session error", 500
    if request.args["state"] != session["auth_state"]:
        return "attack detected :)", 500

    # with this authorization code we can fetch an access token
    url = f"{config.OIDC_URL}/token"
    data = {
        "grant_type": "authorization_code",
        "code": request.args["code"],
        "redirect_uri": config.OIDC_REDIRECT_URL,
        "client_id": config.OIDC_CLIENT_ID,
        "client_secret": config.OIDC_CLIENT_SECRET,
        "state": request.args["state"]
    }
    resp = requests.post(url, data=data)
    resp.raise_for_status()

    data = resp.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"
    access_token = data["access_token"]

    # fetch user information with the access token
    url = f"{config.OIDC_URL}/userinfo"

    try:
        resp = requests.post(url, headers={"Authorization": f"Bearer {access_token}"})
        resp.raise_for_status()
        user_profile = resp.json()
    except:
        return resp.content, 500

    # user can now visit /secret
    session["auth"] = user_profile
    return redirect(url_for("index"))