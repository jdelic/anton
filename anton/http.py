# -* coding: utf-8 *-
import functools
import logging
import events
from anton import config

from gevent.pywsgi import WSGIServer, WSGIHandler

"""
This module provides the glue between `events` and functions which handle HTTP connections. HTTP handlers are
registered through the `@http.register` decorator.

It also includes the GEvent-based HTTP server firing events through `events.fire`. The HTTP server is set up
in such a way that it provides a reference to Anton's `irc_client` instance in the `context` parameter. This
allows Anton HTTP handlers to directly talk to the IRC server Anton is connected to.
"""

_log = logging.getLogger(__name__)

HANDLERS = []


def _save_http_handler(handlerfn):
    HANDLERS.append(handlerfn)


def register(url_regex):
    """
    Returns a decorator that registers a handler for all URLs called on anton's built-in HTTP
    server matching ``url_regex``. If anton's HTTP server receives a HTTP request for a URL
    that matches ``url_regex`` the handler will be called with the following arguments:

    .. code-block:: python

        @http.register(re.compile("^/blah$"))
        def blah_handler(env, regex_match, irc_instance):
            pass

      * env is the WSGI environment dictionary

      * regex_match is the result of ``url_regex.match([called URL])`` and can be used to retrieve
        URL parameters

      * irc_instance is a reference to a connected instance of ``anton.irc_client.IRC`` allowing
        HTTP handlers to directly perform any IRC action such as sending private messages or posting
        messages to an IRC channsel.
    """
    def decorate(handler):
        @functools.wraps(handler)
        def request_handler(context, env):
            path = env["PATH_INFO"]
            if path.startswith(config.HTTP_ROOT):
                path = path[len(config.HTTP_ROOT):]

            regex_match = url_regex.match(path)
            if not regex_match:
                return events.CONTINUE

            result = handler(env, regex_match, context['irc'])
            if result is None:
                return events.CONTINUE

            try:
                content_type, value = result
            except TypeError:
                content_type, value = "text/plain", result

            http_callback = context['callback']
            http_callback(value, headers=[("Content-Type", content_type)])
            return events.STOP

        _save_http_handler(request_handler)
        return request_handler

    return decorate


@events.register("http")
def _http_handler(eventtype, context, env):
    try:
        for handler in HANDLERS:
            r = handler(context, env)
            if r == events.STOP:
                break
    except Exception as e:
        _log.error(e, exc_info=True)
        context['callback']("An error occured (%s). Please check the log." % e, response_line="500 SERVER ERROR")


# Implement some sane logging for gevent.pywsgi so it respects config.logging
class LoggingWSGIHandler(WSGIHandler):
    def __init__(self, *args, **kwargs):
        self.error_logger = _log
        self.request_logger = logging.getLogger("anton.http.requests")
        super(LoggingWSGIHandler, self).__init__(*args, **kwargs)

    def log_error(self, msg, *args):
        self.error_logger.error(msg, *args)

    def log_request(self):
        self.request_logger.info(self.format_request())


class LoggingWSGIServer(WSGIServer):
    handler_class = LoggingWSGIHandler


def server(irc):
    """
    The HTTP server greenlet. This function returns a gevent.pywsgi.WSGIServer instance
    which Anton's main() then runs as the event loop consumer through its serve_forever
    method.
    """
    def application(env, start_response):
        response = [None]

        def callback(data, response_line="200 OK", headers=None):
            if headers is None:
                headers = [("Content-Type", "text/plain")]

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

    s = LoggingWSGIServer(config.HTTP_LISTEN, application)
    return s
