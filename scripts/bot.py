#!/usr/bin/env python
from __future__ import absolute_import, print_function

import fcntl
import sys
import gevent
import gevent.monkey
import os
import logging
import logging.config
from anton import http, scheduler
import anton.config as config
from anton import irc_client as irc


gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()
gevent.monkey.patch_dns()


def main():
    irc_instance = irc.irc_instance()
    http_instance = http.server(irc_instance)
    gevent.spawn(irc.client, irc_instance)
    scheduler.setup(irc_instance)

    # Abuse WSGIServer's serve_forever() implementation as a "daemonization
    # kit" that handles signals correctly.
    _log.info("anton listening on %s:%s" % (config.HTTP_LISTEN[0], config.HTTP_LISTEN[1],))
    http_instance.serve_forever()


if __name__ == "__main__":
    logging.config.dictConfigClass(config.LOGGING).configure()  # set up logging!
    _log = logging.getLogger(__name__)

    def log_bubbledup_exception(type, value, traceback):
        # this will go to sentry if config.SENTRY_DSN is set and stdout
        _log.critical("%s: %s" % (type, value), exc_info=True)

    sys.excepthook = log_bubbledup_exception

    if not os.path.exists(config.DATA_PATH):
        _log.error("config.DATA_PATH (%s) does not exist or can't be read." % config.DATA_PATH)
        sys.exit(1)

    with open(os.path.join(config.DATA_PATH, ".lock"), "w") as f:
        try:
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError, e:
            _log.error("already running, exiting...", exc_info=True)
            sys.exit(1)
        try:
            # this import is necessary to activate all plugins
            from anton import modules
            main()
        except Exception as e:
            # give Sentry/Raven a chance to do some logging
            _log.error("Anton encountered an error", exc_info=True)
            raise
        finally:
            fcntl.lockf(f, fcntl.LOCK_UN)

