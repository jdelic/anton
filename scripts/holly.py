#!/usr/bin/env python

import fcntl
import sys
import gevent
import gevent.monkey
import os
from anton import http
from anton.log import *

# this import is necessary to activate all plugins
from anton import modules

from anton import config
from anton import irc_client as irc


gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()


def main():
    irc_instance = irc.irc_instance()
    http_instance = http.server(irc_instance)
    gevent.spawn(irc.client, irc_instance)

    # Abuse WSGIServer's serve_forever() implementation as a "daemonization
    # kit" that handles signals correctly.
    LOG("holly listening at %s:%s" % (config.HTTP_LISTEN[0], config.HTTP_LISTEN[1],))
    http_instance.serve_forever()


if __name__ == "__main__":
    with open(os.path.join(config.WORKING_DIR, ".lock"), "w") as f:
        try:
            fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            LOG("already running, exiting...")
            sys.exit(1)
        try:
            main()
        finally:
            fcntl.lockf(f, fcntl.LOCK_UN)
