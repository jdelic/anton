# -* coding: utf-8 *-
from functools import wraps
import logging
import events
from anton import config

from gevent.pywsgi import WSGIServer

"""
This module provides the glue between `events` and functions which handle HTTP connections. HTTP handlers are
registered through the `@http.register` decorator.

It also includes the GEvent-based HTTP server firing events through `events.fire`. The HTTP server is set up
in such a way that it provides a reference to Anton's `irc_client` instance in the `context` parameter. This
allows Anton HTTP handlers to directly talk to the IRC server Anton is connected to.
"""

_log = logging.getLogger(__name__)

HANDLERS = []


def register_raw(fn):
    HANDLERS.append(fn)


def register(r):
    def decorate(fn):
        @wraps(fn)
        def new_fn(context, env):
            path = env["PATH_INFO"]
            if path.startswith(config.HTTP_ROOT):
                path = path[len(config.HTTP_ROOT):]

            m = r.match(path)
            if not m:
                return events.CONTINUE

            result = fn(env, m, context['irc'])
            if result is None:
                return events.CONTINUE

            try:
                content_type, value = result
            except TypeError:
                content_type, value = "text/plain", result

            callback = context['callback']
            callback(value, headers=[("Content-Type", content_type)])
            return events.STOP

        register_raw(new_fn)
        return new_fn

    return decorate


@events.register("http")
def http_handler(type, context, env):
    try:
        for handler in HANDLERS:
            r = handler(context, env)
            if r == events.STOP:
                break
    except Exception as e:
        _log.error(e, exc_info=True)
        context['callback']("An error occured (%s). Please check the log." % e, response_line="500 SERVER ERROR")


def server(irc):
    # does this run in a greenlet?
    def application(env, start_response):
        response = [None]

        def callback(data, response_line="200 OK", headers=[("Content-Type", "text/plain")]):
            if response[0] is None:
                response[0] = data
            else:
                raise Exception("Already called.")
            start_response(response_line, headers)

        events.fire("http", {'callback': callback, 'irc': irc}, env)

        if response[0] is not None:
            return response[0]

        start_response("404 File Not Found", [("Content-Type", "text/plain")])
        return "404 File Not Found"

    s = WSGIServer(config.HTTP_LISTEN, application)
    return s

