import praw
from flask import url_for
from suchwow import config, wownero


class Reddit(object):
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=config.PRAW_CLIENT_ID,
            client_secret=config.PRAW_CLIENT_SECRET,
            user_agent=config.PRAW_USER_AGENT,
            username=config.PRAW_USERNAME,
            password=config.PRAW_PASSWORD
        )
        self.subreddit = "wownero"
        self.meme_flair_id = "2527d518-a96c-11ea-ba87-0e32c68cff8f"

    def post(self, title, url):
        try:
            submission = self.reddit.subreddit(self.subreddit).submit(
                title=title,
                url=url,
                resubmit=False,
                flair_id=self.meme_flair_id
            )
            return submission
        except:
            return False

    def comment(self, submission, comment):
        try:
            _comment = submission.reply(comment)
            return _comment
        except:
            return False

def make_post(post):
    if post.to_reddit:
        print(f"Already posted #{post.id} to Reddit")
        return False
    wallet = wownero.Wallet()
    title = f"SuchWow #{post.id} - {post.title}"
    url = url_for('post.uploaded_file', filename=post.image_name, _external=True)
    _comment = [
        f"Submitter: {post.submitter}\n\n",
        f"Timestamp (UTC): {post.timestamp}\n\n",
        "Show this poster some love by sending WOW to the following address:\n\n",
        f"`{wallet.get_address(account=post.account_index)}`\n\n\n\n",
        f"[View Post]({url_for('post.read', id=post.id, _external=True)})"
    ]
    comment = "".join(_comment)
    reddit_post = Reddit().post(title, url)
    reddit_comment = Reddit().comment(reddit_post, comment)
    if reddit_post:
        post.to_reddit = True
        post.save()
        print(f"Posted #{post.id} to Reddit")
        return True
    else:
        print(f"Unable to post #{post.id} to Reddit")
        return False
