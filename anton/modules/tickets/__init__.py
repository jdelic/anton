# -* encoding: utf-8 *-
import logging
from anton import config
from anton import commands
from anton.util import get_class_from_string


_log = logging.getLogger(__name__)


class TicketProviderErrorResponse(Exception):
    pass


class TicketProvider(object):
    """
    Interface to implement for connectors between anton and
    various ticket providers, i.e. JIRA, GitHub, etc.
    """
    def ticket_search(self, callback, args):
        pass

    def ticket_show(self, callback, args):
        pass

    def ticket_create(self, callback, args):
        pass

    def route_command(self, subcommand, callback, args):
        if subcommand == 'search':
            return self.ticket_search(callback, args)
        elif subcommand == 'show':
            return self.ticket_show(callback, args)
        elif subcommand == 'create':
            return self.ticket_create(callback, args)

        return "Unrecognised !ticket subcommand: %s" % subcommand


c_provider = get_class_from_string(config.TICKET_PROVIDER)
provider = c_provider()

@commands.register("!ticket")
def ticket(callback, args):
    tokens = args.split()
    if len(tokens) < 2:
        return "Not enough arguments"
    subcommand = tokens[0]
    subargs = tokens[1:]

    result = None
    try:
        result = provider.route_command(subcommand, callback, subargs)
    except TicketProviderErrorResponse as e:
        _log.error(e, exc_info=True)
        return e
    return result
