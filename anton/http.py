import events
import gevent
import traceback
from anton import config

from gevent.pywsgi import WSGIServer

HANDLERS = []


def register_raw(fn):
    HANDLERS.append(fn)


def register(r):
    def decorate(fn):
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
def http_handler(type, callback, env):
    try:
        for handler in HANDLERS:
            r = handler(callback, env)
            if r == events.STOP:
                break
    except Exception, e:
        traceback.print_exc()
        callback("exception occured:\n" + traceback.format_exc())


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

