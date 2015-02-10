
import os
import sys

DATA_PATH = os.getenv("DATA_PATH", "./data/")
IRC_SERVER = os.getenv("IRC_SERVER", "127.0.0.1")
IRC_PORT = os.getenv("IRC_PORT", "6667")
BACKEND = IRC_SERVER, int(IRC_PORT)
HTTP_ROOT = "/bot"
HTTP_BINDADDRESS = os.getenv("HTTP_BINDADDRESS", "127.0.0.1")
HTTP_PORT = os.getenv("HTTP_PORT", "8000")
HTTP_LISTEN = HTTP_BINDADDRESS, int(HTTP_PORT)

BOT_USERNAME = os.getenv("BOT_USERNAME", "antonia")
BOT_REALNAME = os.getenv("BOT_REALNAME", "antonia")
BOT_NICKNAME = os.getenv("BOT_NICKNAME", "antonia")
BOT_CHANNELS = os.getenv("BOT_CHANNELS", "#twilightzone")

JENKINS_CHANNEL = os.getenv("JENKINS_CHANNEL", "#twilightzone")

TICKET_PROVIDER = os.getenv("TICKET_PROVIDER", "")

GITHUB_CHANNEL = os.getenv("GITHUB_CHANNEL", "#twilightzone")
GITHUB_AUTH_TOKEN = os.getenv("GITHUB_AUTH_TOKEN", "")
GITHUB_DEFAULT_ORGANIZATION = os.getenv("GITHUB_DEFAULT_ORGANIZATION", "laterpay")
GITHUB_DEFAULT_REPO = os.getenv("GITHUB_DEFAULT_REPO", "laterpay")

JIRA_URL = os.getenv("JIRA_URL", "")
JIRA_AUTH_TOKEN = os.getenv("JIRA_AUTH_TOKEN", "")
JIRA_AUTH_SECRET = os.getenv("JIRA_AUTH_SECRET", "")
JIRA_AUTH_ID = os.getenv("JIRA_AUTH_ID", "anton")
JIRA_AUTH_PRIVATEKEY = os.getenv("JIRA_AUTH_PRIVATEKEY", "")

GOOGLE_HANGOUT_CLIENT_ID = os.getenv("GOOGLE_HANGOUT_CLIENT_ID", "")
GOOGLE_HANGOUT_CLIENT_SECRET = os.getenv("GOOGLE_HANGOUT_CLIENT_SECRET", "")
GOOGLE_HANGOUT_REFRESH_TOKEN = os.getenv("GOOGLE_HANGOUT_REFRESH_TOKEN", "")
GOOGLE_HANGOUT_CALENDAR_ID = os.getenv("GOOGLE_HANGOUT_CALENDAR_ID", "primary")
GOOGLE_HANGOUT_DEFAULT_LENGTH = os.getenv("GOOGLE_HANGOUT_DEFAULT_LENGTH", str(60 * 60 * 2))  # 2 hours in seconds

DISABLED_BUILTINS = [s.strip() for s in os.getenv("DISABLED_BUILTINS", "").split(",") if s.strip() != '']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
    },

    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s'
        },
    },

    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,   # this will not work on Python 2.6, where you must set "strm"
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': os.environ.get('SENTRY_DSN', ''),
        },
    },

    'loggers': {
        'sentry.errors': {
            'handlers': ['console'],
            'propagate': False
        },
        'anton.http.requests': {
            'handlers': ['console'],
            'propagate': False,
        },
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

