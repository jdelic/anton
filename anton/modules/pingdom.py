import json
import re
import urlparse
from anton import http, config


class PingdomException(Exception):
    pass

@http.register(re.compile("^/pingdom/post-receive$"))
def http_handler(env, m, irc):

    try:
        content_length = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        content_length = 0

    body = env['QUERY_STRING']
    data = urlparse.parse_qs(body)

    content_type = 'text/plain'
    try:
        message = json.loads(data['message'][0])
    except ValueError:
        raise PingdomException("expecting message query param to be valid json")

    try:
        check = message['check']
        checkname = message['checkname']
        host = message['host']
        action = message['action']
        incidentid = message['incidentid']
        description = message['description']
        body = '[Pingdom] Check {} is {} - {} (Incident #{}) https://my.pingdom.com/'.format(checkname, description, host, incidentid)
    except KeyError:
        raise PingdomException("expecting check, checkname, host, action, incidentid and description keys in json")

    output = body.encode('utf-8')
    irc.chanmsg(config.PINGDOM_CHANNEL, output)
    return "application/json", json.dumps(message)
