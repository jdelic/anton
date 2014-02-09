# -* coding: utf-8 *-
from __future__ import absolute_import
import logging
import re
from anton import config
from jira.client import JIRA
from anton.modules.tickets import TicketProvider, TicketProviderErrorResponse


_log = logging.getLogger(__name__)


class JiraTicketProvider(TicketProvider):
    def __init__(self):
        for k in ['JIRA_AUTH_TOKEN', 'JIRA_AUTH_SECRET', 'JIRA_AUTH_PUBKEY', 'JIRA_AUTH_ID', 'JIRA_URL']:
            if not hasattr(config, k):
                raise TicketProviderErrorResponse("No value for config.%s, no !ticket for you :(" % k)
        options = {
            'server': config.JIRA_URL,
        }
        oauth = {
            'access_token': config.JIRA_AUTH_TOKEN,
            'access_token_secret': config.JIRA_AUTH_SECRET,
            'consumer_key': config.JIRA_AUTH_ID,
            'key_cert': config.JIRA_AUTH_PUBKEY
        }
        self.url = "%s/" % config.JIRA_URL if not config.JIRA_URL.endswith('/') else config.JIRA_URL
        self.jira = JIRA(options=options, oauth=oauth)

    def route_command(self, subcommand, callback, args):
        if subcommand == "jql":
            return self.ticket_jql(callback, args)
        else:
            return super(JiraTicketProvider, self).route_command(subcommand, callback, args)

    def ticket_create(self, callback, args):
        return "create: not implemented yet"

    def ticket_search(self, callback, args):
        return "search: not implemented yet"

    def ticket_show(self, callback, args):
        issue_id = args[0]
        if re.match("[A-Za-z0-9]{0,4}-[0-9]+", issue_id):
            issue = self.jira.issue(issue_id, fields='summary')
            return '%s: %s (%sbrowse/%s)' % (issue.key, issue.fields.summary, self.url, issue.key)
        else:
            return "%s does not match [A-Za-z0-9]{0,4}-[0-9]+ (not a valid JIRA issue id?)" % issue_id

    def ticket_jql(self, callback, args):
        return "jql: not implemented yet"
