#!/usr/bin/env python
from __future__ import absolute_import, print_function

import fcntl
import sys
import gevent
import gevent.monkey
import os
import logging
import logging.config
from anton import http

# this import is necessary to activate all plugins
from anton import modules

import anton.config as config
from anton import irc_client as irc


gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()


def main():
    irc_instance = irc.irc_instance()
    http_instance = http.server(irc_instance)
    gevent.spawn(irc.client, irc_instance)

    # Abuse WSGIServer's serve_forever() implementation as a "daemonization
    # kit" that handles signals correctly.
    _log.info("holly listening at %s:%s" % (config.HTTP_LISTEN[0], config.HTTP_LISTEN[1],))
    http_instance.serve_forever()


if __name__ == "__main__":
    logging.config.dictConfigClass(config.LOGGING).configure()  # set up logging!
    _log = logging.getLogger(__name__)

    with open(os.path.join(config.WORKING_DIR, ".lock"), "w") as f:
        try:
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError, e:
            _log.error("already running, exiting...", e)
            sys.exit(1)
        try:
            main()
        finally:
            fcntl.lockf(f, fcntl.LOCK_UN)
