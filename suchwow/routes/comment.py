from flask import render_template, Blueprint, flash
from flask import request, redirect, url_for, session
from suchwow.models import Post, Comment, Profile
from suchwow.utils.decorators import login_required


bp = Blueprint("comment", "comment")

@bp.route("/comment/create/post/<post_id>", methods=["GET", "POST"])
@login_required
def create(post_id):
    if not Post.filter(id=post_id):
        flash("WTF, that post doesn't exist. Stop it, hackerman.")
        return redirect(url_for("index"))

    if request.method == "POST":
        comment_text = request.form.get("comment")
        if len(comment_text) > 300:
            flash("WTF, too many characters to post, asshole.")
            return redirect(request.url)
        commenter = Profile.get(username=session["auth"]["preferred_username"])
        post = Post.get(id=post_id)
        c = Comment(
            comment=comment_text,
            commenter=commenter,
            post=post,
        )
        c.save()
        return redirect(url_for("post.read", id=post_id))
    return render_template("comment/create.html")
