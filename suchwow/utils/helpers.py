import pickle
from os import path, remove
from datetime import datetime, timedelta
from requests import post as r_post
from json import dumps
from flask import session, current_app
from suchwow.models import Moderator, Post
from suchwow.wownero import Wallet
from suchwow import config


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in config.ALLOWED_EXTENSIONS

def is_moderator(username):
    m = Moderator.filter(username=username)
    if m:
        return True
    else:
        return False

def get_session_user():
    if "auth" not in session or not session["auth"]:
        return None
    return session["auth"]["preferred_username"].strip()

def post_webhook(msg):
    try:
        if current_app.config["DEBUG"]:
            msg = "[DEBUG] " + msg
        data = {
            "text": msg,
            "channel": config.MM_CHANNEL,
            "username": config.MM_USERNAME,
            "icon_url": config.MM_ICON
        }
        res = r_post(config.MM_ENDPOINT, data=dumps(data))
        res.raise_for_status()
        return True
    except:
        return False

def get_latest_tipped_posts():
    key_name = 'latest_tips'
    tipped_posts = rw_cache(key_name, None, 1200)

    if not tipped_posts:
        new_data = []
        w = Wallet()
        data = {}
        for acc in w.accounts():
            txes = w.transfers(acc)
            if 'in' in txes:
                for tx in txes['in']:
                    p = Post.select().where(
                        Post.account_index==acc
                    ).first()
                    if p:
                        data[tx['timestamp']] = p

        dates = sorted(data, reverse=True)
        for d in dates:
            if not data[d] in new_data:
                new_data.append(data[d])

        tipped_posts = rw_cache(key_name, new_data, 1200)

    return tipped_posts


# Use hacky filesystem cache since i dont feel like shipping redis
def rw_cache(key_name, data=None, diff_seconds=3600):
    pickle_file = path.join(config.DATA_FOLDER, f'{key_name}.pkl')
    try:
        if path.isfile(pickle_file):
            mtime_ts = path.getmtime(pickle_file)
            mtime = datetime.fromtimestamp(mtime_ts)
            now = datetime.now()
            diff = now - mtime
            # If pickled data file is less than an hour old, load it and render page
            # Otherwise, determine balances, build json, store pickled data, and render page
            if diff.seconds < diff_seconds:
                print(f'unpickling {key_name}')
                with open(pickle_file, 'rb') as f:
                    pickled_data = pickle.load(f)
                    return pickled_data
            else:
                if data:
                    print(f'pickling {key_name}')
                    with open(pickle_file, 'wb') as f:
                        f.write(pickle.dumps(data))
                        return data
                else:
                    return None
        else:
            if data:
                print(f'pickling {key_name}')
                with open(pickle_file, 'wb') as f:
                    f.write(pickle.dumps(data))
                    return data
            else:
                return None
    except:
        return None
