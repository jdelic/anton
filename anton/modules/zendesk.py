import json
import re
import urlparse
from anton import http, config

class ZendeskException(Exception):
    pass

@http.register(re.compile("^/zendesk/post-receive$"))
def http_handler(env, m, irc):

    try:
        content_length = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        content_length = 0

    body = env['wsgi.input'].read(content_length)
    data = urlparse.parse_qs(body)
    #print data
    content_type = 'text/plain'
    try:
        message = json.loads( data['message'][0] )
    except ValueError:
        raise PingdomException("expecting message query param to be valid json")

    try:
        ticket_status = message['status']
        ticket_id = message['id']
        ticket_timestamp = message['updated_at']
        body = '[Zendesk] Status: {} (Ticket #{}) https://laterpay.zendesk.com/agent/tickets/{} - Timestamp: {}'.format(ticket_status, ticket_id, ticket_id, ticket_timestamp)
    except KeyError:
        raise ZendeskException("expecting status, id, updated_at keys in json")

    output = body.encode('utf-8')
    irc.chanmsg(config.ZENDESK_CHANNEL, output)
    return "application/json", json.dumps(message)
