#!/bin/sh

Pfrom .. ATH=/usr/local/bin:/usr/bin:/bin:/usr/games
PID=$(pgrep -f "python .*holly.py")
if [ "x$PID" != "x" ]; then
  echo already running
  exit 1
fi

if [ "$1" != "run" ]; then
  SCREENLIST=$(screen -list | grep holly | grep "^\s")
  if [ "x$SCREENLIST" != "x" ]; then
    echo screen already running
    exit 1
  fi

  screen -dmS holly $0 run
else
  cd /home/holly/holly
  ulimit -c 999999999
  . /home/holly/holly_virtualenv/bin/activate
  while true
  do
    python holly.py 2>&1 | tee -a holly.log
    echo holly crashed, restarting in 5 seconds >> holly.log
    echo holly crashed, restarting in 5 seconds
    sleep 5
  done
fi

