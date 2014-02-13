import logging
from anton import commands

_log = logging.getLogger(__name__)

@commands.register("!debug")
def debug(callback, args):
    tokens = args.split()
    if len(tokens) > 0 and tokens[0] == "log":
        if len(tokens) == 2:
            if tokens[1] == "debug":
                _log.debug("This is a test DEBUG log", exc_info=True, extra={'stack': True})
            if tokens[1] == "info":
                _log.info("This is a test INFO log", exc_info=True, extra={'stack': True})
            if tokens[1] == "warning":
                _log.warning("This is a test WARNING log", exc_info=True, extra={'stack': True})
        elif len(tokens) != 2 or len(tokens) == 2 and tokens[1] == "error":
            _log.error("This is a test error log", exc_info=True, extra={'stack': True})
        return "logged"

    if len(tokens) > 0 and tokens[0] == "raise":
        raise Exception("This is a test exception for Anton's exception handling")

    return "Use !debug (raise|log) (debug|info|warning|error)"
