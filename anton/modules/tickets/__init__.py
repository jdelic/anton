# -* encoding: utf-8 *-
from anton import config
from anton import commands
from anton.util import get_class_from_string


class TicketProviderErrorResponse(Exception):
    def __init__(self, msg):
        self.msg = msg


class TicketProvider(object):
    """
    Interface to implement for connectors between anton and
    various ticket providers, i.e. JIRA, GitHub, etc.
    """
    def ticket_search(self, callback, owner, repo, subargs):
        pass

    def ticket_show(callback, owner, repo, subargs):
        pass

    def ticket_create(callback, owner, repo, subargs):
        pass


c_provider = get_class_from_string(config.TICKET_PROVIDER)
provider = c_provider()

@commands.register("!ticket")
def ticket(callback, args):
    tokens = args.split()
    if len(tokens) < 2:
        return "Not enough arguments"
    subcommand = tokens[0]
    subargs = tokens[1:]

    try:
        if subcommand == 'search':
            return provider.ticket_search(callback, subargs)
        elif subcommand == 'show':
            return provider.ticket_show(callback, subargs)
        elif subcommand == 'create':
            return provider.ticket_create(callback, subargs)
        else:
            return "Unrecognised !ticket subcommand: %s" % subcommand
    except TicketProviderErrorResponse as e:
        # FIXME: handle this by sending it to IRC
        pass
