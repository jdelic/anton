# -* coding: utf-8 *-
"""
A very simple pubsub event router where anything can register an event "name" (in this module called "type") which it
wants to listen to by using the `@events.register` decorator and anything else can call all registered listeners by
calling the `events.fire()` function.

Both `anton.irc_client` and `anton.http` distribute function calls this way when they receive data.
"""

STOP, CONTINUE = True, False

EVENTS = {}


def register(type):
    def decorate(fn):
        EVENTS.setdefault(type, []).append(fn)
        return fn

    return decorate


def fire(type, context, obj):
    for x in EVENTS.get(type, []):
        x(type, context, obj)
