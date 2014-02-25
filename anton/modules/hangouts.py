# -* coding: utf-8 *-

from anton import commands, config

"""
This is a port of Hubot's Google Hangout script
    https://github.com/hubot-scripts/hubot-google-hangouts/blob/master/src/hangouts.coffee
to anton. It uses the web application OAuth2 type, so you have to set up this an account of
this type at the Google Developer console.

Example:
jdelic: !hangout "Guys, let's talk"
anton: I've started a hangout titled "Guys, let's talk". Here's the link: ...

To be able to do this, anton needs access to a Google Calendar through an OAuth token.
"""


CALENDAR_API_SCOPE = "https://www.googleapis.com/auth/calendar"


for k in ['GOOGLE_HANGOUT_OAUTH_TOKEN', 'GOOGLE_HANGOUT_CALENDAR_ID', 'GOOGLE_HANGOUT_OAUTHSECRET',
          'GOOGLE_HANGOUT_CLIENT_ID']:
    if not hasattr(config, k):
        raise Exception("No value for config.%s, no !hangout for you :(" % k)

    @commands.register("!hangout")
    def hangout(callback, msg):
        pass



