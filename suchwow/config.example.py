from os import getenv


OIDC_URL = 'https://login.wownero.com/auth/realms/master/protocol/openid-connect',
OIDC_CLIENT_ID = 'suchwowxxx',
OIDC_CLIENT_SECRET = 'xxxxxxxxxx',
OIDC_REDIRECT_URL = 'http://localhost:5000/auth'
SECRET_KEY = 'yyyyyyyyyyyyy',
SESSION_TYPE = 'filesystem'
DATA_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024
WALLET_HOST = 'localhost'
WALLET_PORT = 8888
WALLET_PROTO = 'http'
WALLET_USER = 'suchwow'
WALLET_PASS = 'zzzzzzzzzzzzzzz'
PRAW_CLIENT_SECRET = 'xxxxxxxx'
PRAW_CLIENT_ID = 'xxxxxxxx'
PRAW_USER_AGENT = 'suchwow-yyyy-python'
PRAW_USERNAME = 'xxxxxxxx'
PRAW_PASSWORD = 'xxxxxxxx'
SERVER_NAME = 'localhost'
DISCORD_URL = 'xxxxxxx'
BANNED_USERS = {'username': 'reason for the ban'}

MM_ICON = getenv('MM_ICON', 'https://funding.wownero.com/static/wowdoge-a.jpg')
MM_CHANNEL = getenv('MM_CHANNEL', 'suchwow')
MM_USERNAME = getenv('MM_USERNAME', 'SuchWow!')
MM_ENDPOINT = getenv('MM_ENDPOINT', 'ppppppppppppppppppppppppp')
