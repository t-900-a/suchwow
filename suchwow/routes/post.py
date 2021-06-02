from datetime import datetime, timedelta
from os import path, remove
from io import BytesIO
from base64 import b64encode
from qrcode import make as qrcode_make
from flask import render_template, Blueprint, request, session, flash
from flask import send_from_directory, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from secrets import token_urlsafe
from suchwow import wownero
from suchwow import config
from suchwow.models import Post, Comment
from suchwow.utils.decorators import login_required, profile_required, moderator_required
from suchwow.utils.helpers import allowed_file, is_moderator, get_session_user
from suchwow.utils.helpers import rw_cache, post_webhook
from suchwow.reddit import make_post
from suchwow.discord import post_discord_webhook


bp = Blueprint("post", "post")

@bp.route("/post/<id>")
def read(id):
    _address_qr = BytesIO()
    qr_code = None
    if Post.filter(id=id):
        wallet = wownero.Wallet()
        post = Post.get(id=id)
        if not post.approved:
            if not is_moderator(get_session_user()):
                flash("That post has not been approved.")
                return redirect("/")
        if wallet.connected:
            address = wallet.get_address(account=post.account_index)
            transfers = wallet.transfers(account=post.account_index)
            qr_uri = f'wownero:{address}?tx_description=suchwow%20post%20{post.id}'
            address_qr = qrcode_make(qr_uri).save(_address_qr)
            qr_code = b64encode(_address_qr.getvalue()).decode()
        else:
            address = "?"
            transfers = "?"
        return render_template(
            "post/read.html",
            post=post,
            address=address,
            transfers=transfers,
            qr_code=qr_code
        )
    else:
        flash("No meme there, brah")
        return redirect(url_for("index"))

@bp.route("/post/create", methods=["GET", "POST"])
@login_required
@profile_required
def create():
    if request.method == "POST":
        submitter = get_session_user()
        if submitter in config.BANNED_USERS:
            reason = config.BANNED_USERS[submitter]
            flash(f"You can't post for now: {reason}")
            return redirect("/")
        post_title = request.form.get("title")
        # check if the post request has the file part
        if "file" not in request.files:
            flash("You didn't upload a caliente meme, bro! You're fuckin up!")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("You didn't upload a caliente meme, bro! You're fuckin up!")
            return redirect(request.url)
        if post_title == "":
            flash("You didn't give your meme a spicy title, bro! You're fuckin up!")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename =  "{}-{}".format(
                token_urlsafe(12),
                secure_filename(file.filename)
            )
            save_path_base = path.join(current_app.config["DATA_FOLDER"], "uploads")
            save_path = path.join(save_path_base, filename)
            file.save(save_path)
            try:
                wallet = wownero.Wallet()
                account_index = wallet.new_account()
            except:
                flash("Suchwow wallet is fucked up! Try again later.")
                return redirect(request.url)
            post = Post(
                title=post_title,
                text=request.form.get("text", ""),
                submitter=submitter,
                image_name=filename,
                account_index=account_index,
                address_index=0
            )
            post.save()
            post.save_thumbnail()
            url = url_for('post.read', id=post.id, _external=True)
            post_webhook(f"New post :doge2: [{post.id}]({url}) by `{submitter}` :neckbeard:")
            flash("New post created and pending approval!")
            return redirect(url_for("index"))
    return render_template("post/create.html")

@bp.route("/post/<id>/approve")
@moderator_required
def approve(id):
    post = Post.get(id=id)
    url = url_for('post.read', id=post.id, _external=True)
    if post:
        if not post.approved:
            post.approved = True
            post.save()
            post_webhook(f"Post [{post.id}]({url}) approved :white_check_mark: by `{get_session_user()}` :fieri_parrot:")
            flash("Approved")
        if current_app.config["DEBUG"] is False:
            # _r = None
            # _d = None
            # if not post.to_reddit:
            #     _r = make_post(post)
            # if not post.to_discord:
            #     _d = post_discord_webhook(post)
            # if _r and _d:
            #     post_webhook(f"Post [{post.id}]({url}) submitted :dab_parrot: to Reddit and Discord.")
            # else:
            #     post_webhook(f"Post [{post.id}]({url}) failed :this-is-fine-fire: to post to socials...Reddit: {_r} - Discord: {_d}")
            post_discord_webhook(post)
            post_webhook(f"Post [{post.id}]({url}) submitted :dab_parrot: to Discord.")
        return redirect(url_for("mod_queue"))
    else:
        flash("You can't approve this")
        return redirect(url_for("index"))

@bp.route("/post/<id>/delete")
@login_required
def delete(id):
    filtered = Post.filter(id=id)
    user = get_session_user()
    is_mod = is_moderator(user)
    if filtered:
        post = filtered.first()
        if user == post.submitter or is_mod:
            save_path_base = path.join(current_app.config["DATA_FOLDER"], "uploads")
            save_path = path.join(save_path_base, post.image_name)
            remove(save_path)
            post.delete_instance()
            post_webhook(f"Post {post.id} deleted :dumpsterfire: by `{user}` :godmode:")
            flash("Deleted that shit, brah!")
            if is_mod:
                return redirect(url_for("mod_queue"))
            else:
                return redirect(url_for("index"))
        else:
            flash("You can't delete a meme you don't own, brah")
            return redirect(url_for("post.read", id=post.id))
    else:
        flash("No meme there, brah")
        return redirect(url_for("index"))

@bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    file_path = path.join(current_app.config["DATA_FOLDER"], "uploads")
    return send_from_directory(file_path, filename)
