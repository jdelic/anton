# -* coding: utf-8 *-
from datetime import datetime, timedelta
import sys
import json
import logging
from apiclient.discovery import build
from apiclient.errors import HttpError
from httplib2 import Http
from oauth2client.client import OAuth2Credentials, AccessTokenRefreshError
import pytz
import requests
import time

from anton import config, commands

"""
This is a port of Hubot's Google Hangout script
    https://github.com/hubot-scripts/hubot-google-hangouts/blob/master/src/hangouts.coffee
to anton. It uses the *device application* OAuth2 type, so you have to set up an account of
this type on your trusty Google Developer console. Choose "other" as the device's OS.

The reason for this is that this module uses the limited input device workflow for authorizing
the needed OAuth2 refresh token. We do it this way so that you can authorize Anton from
any machine without having to run a HTTP endpoint to receive redirects from Google. This
OAuth2 flow is documented here: https://developers.google.com/accounts/docs/OAuth2ForDevices

Authorize Anton like this:
  1. Create device client credentials on your developer console for Anton, choose "Other" as its OS:
        https://console.developers.google.com/
  2. Set anton.config.GOOGLE_HANGOUT_CLIENT_ID to the new ID and
     anton.config.GOOGLE_HANGOUT_CLIENT_SECRET accordingly
  3. Run this module to receive authorization credentials. You'll need internet access for that.
        python -m anton.modules.hangouts
  4. Use your browser to navigate to the provided URL and enter the provided code while Anton polls
     Google for an access token.
  5. Complete the process in under 30 minutes.

NOTE: If you get the error "invalid_client", you have to go to your developer console into
"APIs & auth"->"Consent screen" and set an application name. I recommend "Anton, the IRC bot".

!!! IMPORTANT: You MUST enable "Automatically add video calls to events I create" in Google Calendar's settings !!!

Usage example of this module:
jdelic: !hangout Guys, let's talk
anton: I've started a hangout titled "Guys, let's talk". Here's the link: ...

To be able to do this, anton needs access to a Google Calendar through an OAuth token.
"""


CALENDAR_API_SCOPE = "https://www.googleapis.com/auth/calendar"
TOKEN_URI = "https://accounts.google.com/o/oauth2/token"
_log = logging.getLogger(__name__)

_service = None
_creds = None
_http = Http()
_calendar_id = config.GOOGLE_HANGOUT_CALENDAR_ID if hasattr(config, 'GOOGLE_HANGOUT_CALENDAR_ID') else "primary"
_event_length = int(config.GOOGLE_HANGOUT_DEFAULT_LENGTH) if hasattr(config, 'GOOGLE_HANGOUT_DEFAULT_LENGTH') else 60 * 60 * 2
_configured = False

if not __name__ == "__main__":
    for k in ['GOOGLE_HANGOUT_REFRESH_TOKEN', 'GOOGLE_HANGOUT_CALENDAR_ID', 'GOOGLE_HANGOUT_CLIENT_SECRET',
              'GOOGLE_HANGOUT_CLIENT_ID']:
        if not hasattr(config, k):
            raise Exception("No value for config.%s, no !hangout for you :(" % k)
    # we only have a refresh token... so create credentials with an "expired" access token for later use
    _creds = OAuth2Credentials("", config.GOOGLE_HANGOUT_CLIENT_ID, config.GOOGLE_HANGOUT_CLIENT_SECRET,
                               config.GOOGLE_HANGOUT_REFRESH_TOKEN, datetime(1970, 1, 1), TOKEN_URI, "IRC.Anton/1.0")
    _http = _creds.authorize(_http)

    # validate that we can connect to the calendar
    _log.info("Testing Google credentials for anton.modules.hangouts")
    _service = build('calendar', 'v3', http=_http)
    try:
        c = _service.calendars().get(calendarId=_calendar_id).execute()
    except HttpError as e:
        _log.error("The calendar %s seems to be unavailable" % config.GOOGLE_HANGOUT_CALENDAR_ID,
                   exc_info=True)
    else:
        _configured = True


@commands.register("!hangout")
def hangout(callback, msg):
    global _service, _calendar_id, _event_length

    events = _service.events()
    now = datetime.now(tz=pytz.UTC)
    try:
        ev = events.insert(
            calendarId=_calendar_id,
            body={
                'summary': 'Google Hangout: %s' % msg,
                'description': "",
                'reminders': {
                    'overrides': {
                        'method': 'popup',
                        'minutes': 0
                    }
                },
                'start': {
                    'dateTime': now.isoformat(),
                    'timeZone': 'UTC'
                },
                'end': {
                    'dateTime': (now + timedelta(seconds=_event_length)).isoformat(),
                    'timeZone': 'UTC'
                }
            }
        ).execute()
    except Exception as e:
        _log.error("Couldn't insert event '[Anton] Google Hangout: %s'" % msg, exc_info=True)
        return "Computer says 'No' :(. Try again."

    if "hangoutLink" not in ev:
        return "I created the event, but the connected user has to enable video calls for all events on his " \
               "calendar :(. Sorry."

    return "I've started a Hangout titled \"%s\". Here is the link: %s" % (msg, ev['hangoutLink'])


if __name__ == "__main__":
    for k in ['GOOGLE_HANGOUT_CLIENT_SECRET', 'GOOGLE_HANGOUT_CLIENT_ID']:
        if not hasattr(config, k):
            print("You need to set the environment variables:")
            print("    GOOGLE_HANGOUT_CLIENT_SECRET")
            print("    GOOGLE_HANGOUT_CLIENT_ID")
            print("")
            sys.exit(1)

    print("All config available. This module will now help you create a refresh token.\n")
    print("Contacting Google...")
    resp = requests.post(
        "https://accounts.google.com/o/oauth2/device/code",
        {
            'client_id': config.GOOGLE_HANGOUT_CLIENT_ID,
            'scope': CALENDAR_API_SCOPE
        }
    )
    ds = json.loads(resp.text)
    print("Please go to:    %s" % ds['verification_url'])
    print("Enter this code: %s\n" % ds['user_code'])
    print("I'll wait for you to do this now and detect success automatically... Press Ctrl+C to cancel.\n")

    resp = None
    pr = None
    while True:
        resp = requests.post(
            TOKEN_URI,
            {
                'client_id': config.GOOGLE_HANGOUT_CLIENT_ID,
                'client_secret': config.GOOGLE_HANGOUT_CLIENT_SECRET,
                'code': ds['device_code'],
                'grant_type': 'http://oauth.net/grant_type/device/1.0'
            }
        )
        pr = json.loads(resp.text)
        if 'error' in pr:
            if pr['error'] != 'authorization_pending':
                print("received unknown error: %s" % pr['error'])
                print("debug info:\n%s" % resp.text)
            time.sleep(ds['interval'])  # honor Google's polling interval
        else:
            break

    if 'refresh_token' in pr:
        print("\nGot the response. Add the following refresh token to your Anton config:\n")
        print("Refresh token: %s\n" % pr['refresh_token'])
        print("Thanks. You're done here :).")
    else:
        print("For some reason Google's response doesn't contain a refresh token. I'm going to")
        print("output the full response for you to figure out:\n")
        print(resp.text)
        print("")
