from datetime import datetime, timedelta
from os import path
from flask import render_template, Blueprint, request, session, flash
from flask import send_from_directory, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from suchwow import wownero
from suchwow.models import Post
from suchwow.utils.helpers import rw_cache


bp = Blueprint("leaderboard", "leaderboard")

@bp.route("/leaderboards/top_posters")
def top_posters():
    top_posters = {}
    posts = rw_cache('top_posters')
    if not posts:
        posts = Post.select().where(Post.approved==True)
        for post in posts:
            transfers = []
            incoming = wownero.Wallet().incoming_transfers(post.account_index)
            if "transfers" in incoming:
                for xfer in incoming["transfers"]:
                    transfers.append(wownero.from_atomic(xfer["amount"]))
            total = sum(transfers)
            if post.submitter not in top_posters:
                top_posters[post.submitter] = {"amount": 0, "posts": []}

            top_posters[post.submitter]["amount"] += float(total)
            top_posters[post.submitter]["posts"].append(post)
        rw_cache('top_posters', top_posters)
    else:
        top_posters = posts

    return render_template("leaderboard.html", posters=top_posters)

@bp.route("/leaderboards/top_posts")
def top_posts():
    top_posts = []
    days = request.args.get('days', 1)
    try:
        days = int(days)
    except:
        days = 1

    if days not in [1, 3, 7, 30]:
        days = 7

    hours = 24 * days
    diff = datetime.now() - timedelta(hours=hours)
    key_name = f'top_posts_{str(hours)}'

    posts = rw_cache(key_name)
    if not posts:
        posts = Post.select().where(
            Post.approved==True,
            Post.timestamp > diff
        ).order_by(
            Post.timestamp.desc()
        )
        for post in posts:
            p = post.show()
            if isinstance(p['received_wow'], float):
                top_posts.append(p)

        posts = rw_cache(key_name, top_posts)

    return render_template("post/top.html", posts=posts, days=days)
