import requests
from flask import url_for
from random import choice
from suchwow import config
from suchwow import wownero


intro = ["Whatup", "What is up", "What the fuck is up", "What in the fuck is up", "Yo", "Sup", "What's the haps"]
insults = ["fart sacks", "dick lips", "shit stains", "chodes", "dipshits", "dick nipples", "turd burglars", "shit birds", "meat sticks", "meat puppets", "turkey necks", "dick nibblers", "shit lips"]


def post_discord_webhook(post):
    try:
        wallet = wownero.Wallet()
        post_wow_address = wallet.get_address(account=post.account_index)
        content = f"{choice(intro)} {choice(insults)}, new SuchWow post #{post.id} by {post.submitter} is up! {url_for('post.read', id=post.id, _external=True)}"
        msg = {"content": content}
        discord_webhook_url = config.DISCORD_URL
        r = requests.post(discord_webhook_url, data=msg)
        r.raise_for_status()
        post.to_discord = True
        post.save()
        return True
    except:
        return False
