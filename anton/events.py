# -* coding: utf-8 *-
"""
A very simple pubsub event router where anything can register an event "name" (in this module called "type") which it
wants to listen to by using the `@events.register` decorator and anything else can call all registered listeners by
calling the `events.fire()` function.

Both `anton.irc_client` and `anton.http` distribute function calls this way when they receive data.
"""

STOP, CONTINUE = True, False

EVENTS = {}


def register(event_type):
    """
    Register a handler for events of the type ``event_type``, where ``event_type`` is just a
    string compared to the ``event_type`` parameter passed to calls to ``events.fire()``.
    """
    def decorate(handler):
        EVENTS.setdefault(event_type, []).append(handler)
        return handler

    return decorate


def fire(event_type, event_context, event_args):
    """
    Call all handlers registered using @events.register(event_type) for ``event_type`` in a loop
    and pass them arbitrary context and event argument information. The content of these
    parameters differs depending on the module raising the event. See ``anton.irc_client`` and
    ``anton.http`` for more information.
    """
    for handler in EVENTS.get(event_type, []):
        handler(event_type, event_context, event_args)
