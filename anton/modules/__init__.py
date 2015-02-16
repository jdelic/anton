# -* coding: utf-8 *-
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
    'tickets',
    'debug',
    'github',
    'hangouts',
    'pandora',
    'eightball',
]


def init_modules():
    for module in _BUILTIN_MODULES:
        if module not in config.DISABLED_BUILTINS:
            import_module("%s.%s" % ("anton.modules", module))

    # load external modules
    for module in pkg_resources.iter_entry_points("anton.external.modules"):
        module.load()
