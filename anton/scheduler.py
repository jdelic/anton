# -* coding: utf-8 *-
from datetime import datetime
from functools import wraps
import logging
from croniter.croniter import croniter
import gevent
import pytz

"""
Provides a simple per-second task scheduler which allows fixed execution with a cron-like interface. If a scheduled
function returns `True` it will be rescheduled for execution, if it returns `False` it will not be rescheduled.

The first parameter passed to a scheduled function will be a reference to the schedule object which handles it,
allowing it to keep simple state. Due to the nature of Anton, there are two ways to communicate with IRC: If the
scheduled job is part of a module, the schedule object will have a valid `anton.irc_client.IRC` instance in
the `irc` attribute. This allows communication with all channels through `IRC.chanmsg`. If the schedule object is
created through a channel message event handler, the `irc` attribute will be `None` and you should use the
callback provided to you through the event handler instead.

The cron format is either 5 or 6 columns with the optional 6th column designating seconds.
  * * * * * *
  | | | | | |
  | | | | | '------ seconds (0-59) [optional]
  | | | | '---------- day of week (0 - 7) (0 to 6 are Sunday to Saturday, or use names; 7 is Sunday, the same as 0)
  | | | '-------------- month (1 - 12)
  | | '------------------ day of month (1 - 31)
  | '---------------------- hour (0 - 23)
  '-------------------------- min (0 - 59)

You can schedule tasks in a pytz timezone, by using the `sched_tz` argument. Otherwise the scheduling timezone
will default to UTC.
::
    import pytz
    from anton.scheduler import schedule
    @schedule('0 14 * * *', sched_tz=pytz.timezone("Europe/Berlin"))
    def scheduled_in_Germany_DST_aware():
        # ... run at 2pm German time
        pass

Examples:
::
    import pytz
    from anton.scheduler import schedule
    from anton import commands
    from datetime import datetime


    @schedule('* * * * * */5', "#twilightzone", "useless ticker")  # execute every 5 seconds
    def useless_clock(sched, channel, clockname):  # clockname will be "useless ticker"
        d = datetime.now(tz=pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        sched.irc.chanmsg(channel, "%s: %s" % (clockname, d))
        return True  # always reschedule


    @commands.register("!schedulertest")  # if you say "!schedulertest", Anton will count from 3 to 1
    def schedulertest(callback, args):
        # run every second for 3 seconds
        @schedule('* * * * * *', 3)
        def tick(sched, ticks):
            if not hasattr(sched, 'ticks'):
                sched.ticks = ticks
            callback("tick %s" % sched.ticks)  # sched.irc is None because the task is created in a command, so we
                                               # use callback() instead
            sched.ticks -= 1
            return sched.ticks > 0             # don't reschedule after the countdown is complete
"""

_jobs = []
_log = logging.getLogger(__name__)
_initialized = False


class schedule(object):
    def __init__(self, cronstr, *args, **kwargs):
        self.cronstr = cronstr
        self.args = args
        self.kwargs = kwargs
        self.task = None
        self.irc = None
        self._scheduled = False

        if "sched_tz" in kwargs:
            self.sched_tz = kwargs["sched_tz"]
        else:
            self.sched_tz = pytz.UTC

        try:
            croniter(self.cronstr)
        except ValueError:
            _log.error("Invalid cron string '%s' for task %s" % (self.cronstr, str(self.task)), exc_info=True)

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # schedule the next execution if fn returns True
            ret = fn(self, *args, **kwargs)
            if ret:
                self.set_alarm()

        self.task = wrapper
        _jobappend(self)

        # we don't really change the wrapped function's functionality, so we return the original
        return fn

    def set_alarm(self, irc=None):
        if self._scheduled or self.task is None:
            return

        if irc is not None:
            self.irc = irc

        base = datetime.now(tz=self.sched_tz)
        delta = croniter(self.cronstr, base).get_next(datetime) - base
        # wait at least 1 second
        secs = 1 if delta.seconds == 0 else delta.seconds
        _log.debug("Scheduling %s for execution in %s seconds" % (str(self.task), secs))
        # schedule async execution in the event loop
        gevent.spawn_later(secs, self.task, *self.args, **self.kwargs)


def _jobappend(job):
    _jobs.append(job)
    if _initialized:
        _log.debug("Adding new job %s" % str(job))
        job.set_alarm()


def setup(irc_instance):
    global _initialized
    _log.info("Scheduler starting with %s jobs" % len(_jobs))
    for job in _jobs:
        job.set_alarm(irc_instance)
    _initialized = True
