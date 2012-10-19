import irc_client as irc
import os

BACKEND = os.getenv("IRC_SERVER_HOST"), int(os.getenv("IRC_SERVER_PORT"))
HTTP_ROOT = "/bot"
HTTP_LISTEN = "0.0.0.0", int(os.getenv("PORT"))

BOT_USERNAME = "anton"
BOT_REALNAME = "anton"
BOT_NICKNAME = "anton"
#BOT_CHANNELS = ("#twilightzone", "#laterpay",)
JENKINS_CHANNEL = os.getenv("JENKINS_CHANNEL")
BOT_CHANNELS = ("#twilightzone", )
