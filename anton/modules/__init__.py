# -* coding: utf-8 *-
import logging
import pkg_resources
from anton import config
from anton.util import import_module

_BUILTIN_MODULES = [
    'learndb',
    'thanks',
    'google',
    'zalgo',
    'slogan',
    'title_fetcher',
    'jenkins',
    'huzzah',
    'spin',
    'tickets',
    'debug',
    'github',
    'hangouts',
    'pandora',
    'eightball',
]


_log = logging.getLogger(__name__)


def init_modules():
    for module in _BUILTIN_MODULES:
        if module not in config.DISABLED_BUILTINS:
            _log.info("Loading builtin module: %s", module)
            import_module("%s.%s" % ("anton.modules", module))

    # load external modules
    for module in pkg_resources.iter_entry_points("anton.external.modules"):
        _log.info("Loading external module: %s", module)
        module.load()
