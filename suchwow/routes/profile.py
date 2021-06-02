from flask import render_template, Blueprint, flash
from flask import request, redirect, url_for, session
from suchwow.models import Profile
from suchwow.utils.decorators import login_required


bp = Blueprint("profile", "profile")

@bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit():
    un = session["auth"]["preferred_username"]
    profile_exists = Profile.filter(username=un)
    if request.method == "POST":
        address = request.form.get("address")
        if len(address) in [97, 108]:
            if profile_exists:
                profile = Profile.get(username=un)
                profile.address = address
                profile.save()
            else:
                profile = Profile(
                    username=un,
                    address=address
                )
                profile.save()
            return redirect(request.args.get("redirect", "/"))
        else:
            flash("WTF bro, that's not a valid Wownero address")
            return redirect(request.url)
    if profile_exists:
        profile = Profile.get(username=un)
    else:
        profile = None
    return render_template("profile/edit.html", profile=profile)
