import json
import click
import arrow
from math import ceil
from datetime import datetime, timedelta
from random import choice
from os import makedirs, path, remove
from flask import Flask, request, session, redirect
from flask import render_template, flash, url_for
from flask_session import Session
from suchwow import config
from suchwow.models import Post, Profile, Comment, Notification, db, Moderator
from suchwow.routes import auth, comment, post, profile, leaderboard, api
from suchwow.utils.decorators import login_required, moderator_required
from suchwow.utils.helpers import post_webhook, get_latest_tipped_posts
from suchwow.reddit import make_post
from suchwow.discord import post_discord_webhook
from suchwow import wownero, filters


app = Flask(__name__)
app.config.from_envvar("FLASK_SECRETS")
app.secret_key = app.config["SECRET_KEY"]
Session(app)

app.register_blueprint(post.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(profile.bp)
app.register_blueprint(comment.bp)
app.register_blueprint(leaderboard.bp)
app.register_blueprint(api.bp)
app.register_blueprint(filters.bp)

@app.route("/")
def index():
    itp = 15
    page = request.args.get("page", 1)
    submitter = request.args.get("submitter", None)
    content = request.args.get("content", None)

    if content == 'latest_tipped':
        posts = get_latest_tipped_posts()
        return render_template(
            "index.html",
            posts=posts[0:30],
            title="Latest Tipped Memes"
        )

    try:
        page = int(page)
    except:
        flash("Wow, wtf hackerman. Cool it.")
        page = 1

    posts = Post.select().where(Post.approved==True).order_by(Post.timestamp.desc())
    if submitter:
        posts = posts.where(Post.submitter==submitter)

    paginated_posts = posts.paginate(page, itp)
    total_pages = ceil(posts.count() / itp)
    return render_template(
        "index.html",
        posts=paginated_posts,
        page=page,
        total_pages=total_pages,
        title="Latest Memes"
    )


@app.route("/mod")
@moderator_required
def mod_queue():
    posts = Post.select().where(Post.approved==False).order_by(Post.timestamp.asc())
    return render_template("index.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found(error):
    flash("nothing there, brah")
    return redirect(url_for("index"))

@app.cli.command("init")
def init():
    # create subdirs
    for i in ["uploads", "db", "wallet"]:
        makedirs(f"{config.DATA_FOLDER}/{i}", exist_ok=True)

    # init db
    db.create_tables([Post, Profile, Comment, Notification, Moderator])

@app.cli.command("post_reddit")
@click.argument('last_hours')
def post_reddit(last_hours):
    posts = Post.select().where(
        Post.approved==True,
        Post.to_reddit==False
    ).order_by(Post.timestamp.asc())
    for p in posts:
        if p.hours_elapsed() < int(last_hours):
            if not p.to_reddit:
                _p = make_post(p)
                if _p:
                    p.to_reddit = True
                    p.save()
                    return

@app.cli.command("create_accounts")
def create_accounts():
    wallet = wownero.Wallet()
    for post in Post.select():
        if post.account_index not in wallet.accounts():
            account = wallet.new_account()
            print(f"Created account {account}")

@app.cli.command("payout_users")
def payout_users():
    wallet = wownero.Wallet()
    _fa = wownero.from_atomic
    _aw = wownero.as_wownero
    for post in Post.select():
        submitter = Profile.get(username=post.submitter)
        balances = wallet.balances(post.account_index)
        url = url_for('post.read', id=post.id, _external=True)
        if balances[1] > 0:
            print(f"Post #{post.id} has {balances[1]} funds unlocked and ready to send. Sweeping all funds to user's address ({submitter.address}).")
            sweep = wallet.sweep_all(account=post.account_index, dest_address=submitter.address)
            print(sweep)
            if "tx_hash_list" in sweep:
                amount = 0
                for amt in sweep["amount_list"]:
                    amount += int(amt)
                # post_webhook(f"Paid out :moneybag: {_aw(_fa(amount))} WOW to `{post.submitter}` for post [{post.id}]({url})")
                # god damn you eimernase, why'd you ruin this for me? :P

@app.cli.command("add_admin")
@click.argument("username")
def add_admin(username):
    if not Moderator.filter(username=username):
        m = Moderator(username=username)
        m.save()
        print(f"Added {username}")
        post_webhook(f"Moderator `{username}` added :ship_it_parrot: by console :black_flag:")
    else:
        print("That moderator already exists")

@app.cli.command("remove_admin")
@click.argument("username")
def remove_admin(username):
    m = Moderator.filter(username=username).first()
    if m:
        m.delete_instance()
        print(f"Deleted {username}")
        post_webhook(f"Moderator `{username}` removed :excuseme: by console :black_flag:")
    else:
        print("That moderator doesn't exist")

@app.cli.command("show")
@click.argument("post_id")
def post_id(post_id):
    p = Post.filter(id=post_id).first()
    if p:
        print(p.show())
    else:
        print("That post doesn't exist")


if __name__ == "__main__":
    app.run()
