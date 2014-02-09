
import os
import sys
import raven


WORKING_DIR = "."
BACKEND = os.getenv("IRC_SERVER_HOST"), int(os.getenv("IRC_SERVER_PORT"))
HTTP_ROOT = "/bot"
HTTP_LISTEN = "0.0.0.0", int(os.getenv("PORT"))

BOT_USERNAME = "antonia"
BOT_REALNAME = "antonia"
BOT_NICKNAME = "antonia"
BOT_CHANNELS = ("#twilightzone", "#laterpay",)
JENKINS_CHANNEL = os.getenv("JENKINS_CHANNEL")
GITHUB_CHANNEL = JENKINS_CHANNEL
GITHUB_AUTH_TOKEN = os.environ['GITHUB_AUTH_TOKEN']
GITHUB_DEFAULT_ORGANIZATION = 'laterpay'
GITHUB_DEFAULT_REPO = 'laterpay'


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
        '': {
            'handlers': ['console', 'sentry'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

