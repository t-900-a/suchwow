from peewee import *
from os import path
from datetime import datetime
from PIL import Image
from suchwow import wownero
from suchwow import config


db = SqliteDatabase(f"{config.DATA_FOLDER}/db/sqlite.db")

class Post(Model):
    id = AutoField()
    title = CharField()
    text = CharField()
    submitter = CharField()
    image_name = CharField()
    readonly = BooleanField(default=False)
    hidden = BooleanField(default=False)
    account_index = IntegerField()
    address_index = IntegerField()
    timestamp = DateTimeField(default=datetime.now)
    reddit_url = CharField(null=True)
    to_reddit = BooleanField(default=False)
    to_discord = BooleanField(default=False)
    approved = BooleanField(default=False)

    def get_image_path(self, thumbnail=False):
        save_path_base = path.join(config.DATA_FOLDER, "uploads")
        if thumbnail:
            save_path = path.join(save_path_base, self.get_thumbnail_name())
        else:
            save_path = path.join(save_path_base, self.image_name)
        return save_path

    def save_thumbnail(self):
        try:
            image = Image.open(self.get_image_path())
            image.thumbnail((200,200), Image.ANTIALIAS)
            image.save(self.get_image_path(True), format=image.format, quality=90)
            image.close()
            return True
        except:
            return False

    def get_thumbnail_name(self):
        s = path.splitext(self.image_name)
        return s[0] + '.thumbnail' + s[1]

    def get_received_wow(self):
        try:
            w = wownero.Wallet()
            it = w.incoming_transfers(self.account_index)
            if 'transfers' in it:
                amounts = [amt['amount'] for amt in it['transfers'] if 'transfers' in it]
                return wownero.as_wownero(wownero.from_atomic(sum(amounts)))
            else:
                return 0
        except:
            return '?'

    def hours_elapsed(self):
        now = datetime.utcnow()
        diff = now - self.timestamp
        return diff.total_seconds() / 60 / 60

    def show(self):
        return {
            'id': self.id,
            'title': self.title,
            'text': self.text,
            'submitter': self.submitter,
            'image_name': self.image_name,
            'image_path': self.get_image_path(),
            'thumbnail_name': self.get_thumbnail_name(),
            'thumbnail_path': self.get_image_path(True),
            'readonly': self.readonly,
            'hidden': self.hidden,
            'account_index': self.account_index,
            'address_index': self.address_index,
            'timestamp': self.timestamp,
            'reddit_url': self.reddit_url,
            'to_reddit': self.to_reddit,
            'to_discord': self.to_discord,
            'approved': self.approved,
            'received_wow': self.get_received_wow(),
            'hours_elapsed': self.hours_elapsed()
        }

    class Meta:
        database = db

class Moderator(Model):
    id = AutoField()
    username = CharField(unique=True)

    class Meta:
        database = db

class Profile(Model):
    id = AutoField()
    username = CharField()
    address = CharField()
    notifications = IntegerField(default=0)

    class Meta:
        database = db

class Comment(Model):
    id = AutoField()
    comment = TextField()
    commenter = ForeignKeyField(Profile)
    post = ForeignKeyField(Post)
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = db

class Notification(Model):
    type = CharField()
    message = TextField()
    username = ForeignKeyField(Profile)
    timestamp = DateTimeField(default=datetime.now)

    class Meta:
        database = db
