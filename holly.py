#!/usr/bin/env python

import fcntl
import sys
import gevent

import modules

import irc
import http

from log import *
from gevent import socket, monkey
from gevent.pywsgi import WSGIServer

monkey.patch_socket()

def main():
  gevent.spawn(http.server)
#  gevent.spawn(irc.client)

  irc.client() # HACK

  while True:
    gevent.core.loop()

if __name__ == "__main__":
  with open(".lock", "w") as f:
    try:
      fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
      LOG("already running, exiting...")
      sys.exit(1)
    try:  
      main()
    finally:
     fcntl.lockf(f, fcntl.LOCK_UN)
