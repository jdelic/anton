#!/usr/bin/env python

import fcntl
import sys
import gevent
import os

import modules

from config import irc as irc
import config
import http

from log import *
from gevent import monkey

monkey.patch_socket()
monkey.patch_ssl()

def main():
  irc_instance = irc.irc_instance()
  gevent.spawn(http.server, irc_instance)
#  gevent.spawn(irc.client)

  irc.client(irc_instance) # HACK

#  while True:
#    gevent.core.loop()

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
