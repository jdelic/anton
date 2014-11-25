import json
import re
import urlparse
from anton import http, config


@http.register(re.compile("^/pingdom/post-receive$"))
def http_handler(env, m, irc):

    try:
        content_length = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        content_length = 0

    body = env['QUERY_STRING']
    data = urlparse.parse_qs(body)

    content_type = {'Content-Type': 'text/plain'}
    try:
        message = json.loads( data['message'][0] )
    except ValueError:
        return 'expecting message query param to be valid json', 400, content_type

    try:
        check = message['check']
        checkname = message['checkname']
        host = message['host']
        action = message['action']
        incidentid = message['incidentid']
        description = message['description']
        body = '[Pingdom] Check {} is {} - {} (Incident #{}) https://my.pingdom.com/'.format(checkname, description, host, incidentid)
    except KeyError:
        return 'expecting check, checkname, host, action, incidentid and description keys', 400, content_type

    output = body.encode('utf-8')
    irc.chanmsg(config.PINGDOM_CHANNEL, output)
    return "application/json", json.dumps(message)
