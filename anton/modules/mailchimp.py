import json
import re
import urllib
import urlparse
from anton import http, config

class MailChimpException(Exception):
    pass

@http.register(re.compile("^/mailchimp/post-receive$"))
def http_handler(env, m, irc):

    try:
        content_length = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        content_length = 0

    request_body = env['wsgi.input'].read()
    wsgi = urlparse.parse_qs(request_body)

    body = env['QUERY_STRING']
    if body == "":
        return "application/json", body
    data =  urllib.unquote(body).decode('utf8')

    print env
    print wsgi
    print body
    print data

    content_type = 'text/plain'
    try:
        message = json.loads(data)
    except ValueError:
        raise MailChimpException("expecting valid json")

    # https://apidocs.mailchimp.com/webhooks/
    try:
        type = message['type']
        if type == "subscribe":
            fired_at = message['fired_at']
            data_id = message['data[id]']
            data_list_id = message['data[list_id]']
            data_email = message['data[email]']
            data_email_type = message['data[email_type]']
            data_merges_email = message['data[merges][EMAIL]']
            data_merges_fname = message['data[merges][FNAME]']
            data_merges_lname = message['data[merges][LNAME]']
            data_merges_interests = message['data[merges][INTERESTS]']
            data_ip_opt = message['data[ip_opt]']
            data_ip_signup = message['data[ip_signup]']
            body = '[MailChimp] {} subscribed to {} - https://us3.admin.mailchimp.com/lists/members/?id={}'.format(data_email, data_list_id, data_id)
        elif type == "unsubscribe":
            fired_at = message['fired_at']
            data_action = message['data[action]']
            data_reason = message['data[reason]']
            data_id = message['data[id]']
            data_list_id = message['data[list_id]']
            data_email = message['data[email]']
            data_email_type = message['data[email_type]']
            data_merges_email = message['data[merges][EMAIL]']
            data_merges_fname = message['data[merges][FNAME]']
            data_merges_lname = message['data[merges][LNAME]']
            data_merges_interests = message['data[merges][INTERESTS]']
            data_ip_opt = message['data[ip_opt]']
            data_campaign_id = message['data[campaign_id]']
            data_reason2 = message['data[reason]']
            body = '[MailChimp] {} - {} - Unsubscribed from {} - https://us3.admin.mailchimp.com/lists/members/?id={}'.format(data_email, data_reason, data_list_id, data_id)
        elif type == "profile":
            fired_at = message['fired_at']
            data_id = message['data[id]']
            data_list_id = message['data[list_id]']
            data_email = message['data[email]']
            data_email_type = message['data[email_type]']
            data_merges_email = message['data[merges][EMAIL]']
            data_merges_fname = message['data[merges][FNAME]']
            data_merges_lname = message['data[merges][LNAME]']
            data_merges_interests = message['data[merges][INTERESTS]']
            data_ip_opt = message['data[ip_opt]']
            body = '[MailChimp] {} updated profile - https://us3.admin.mailchimp.com/lists/members/?id={}'.format(data_email, data_list_id )
        elif type == "upemail":
            fired_at = message['fired_at']
            data_list_id = message['data[list_id]']
            data_new_id = message['data[new_id]']
            data_new_email = message['data[new_email]']
            data_old_email = message['data[old_email]']
            body = '[MailChimp] {} updated email to {}'.format(data_old_email, data_new_email )
        elif type == "cleaned":
            fired_at = message['fired_at']
            data_list_id = message['data[list_id]']
            data_campaign_id = message['data[campaign_id]']
            data_reason = message['data[reason]']
            data_email = message['data[email]']
            body = '[MailChimp] {} was removed: {}'.format(data_email, data_reason )
        elif type == "campaign":
            fired_at = message['fired_at']
            data_id = message['data[id]']
            data_subject = message['data[subject]']
            data_status = message['data[status]']
            data_reason = message['data[reason]']
            data_list_id = message['data[list_id]']
            body = '[MailChimp] {} {}: {} - {} - {}'.format(type, data_subject, data_status , fired_at, data_reason)
    except KeyError:
        raise MailChimpException("expecting type: subscribe, unsubscribe, profile, upemail, cleaned or campaign in json")

    output = body.encode('utf-8')
    irc.chanmsg(config.MAILCHIMP_CHANNEL, output)
    return "application/json", json.dumps(message)
