import random

from anton import commands
from anton.modules.learndb import lookup


@commands.register('!spin')
def spin(callback, arg):
    """
    Chooses one of the input words.
    If any word starts with a $, the value for that word on learndb is split
    into additional choices.
    """
    choices = arg.split(' ')
    # check if any choice needs to be learndb-expanded (starting with $)
    plain_choices = [c for c in choices if not c.startswith('$')]
    var_choices = [c for c in choices if c.startswith('$')]
    # Expand words
    expansions = []
    for c in var_choices:
        key = c[1:]  # Ignore trailling $
        try:
            val = lookup(key)
            expansions += val.split(' ')
        except KeyError:
            continue

    choices = plain_choices + expansions
    if not choices:
        return 'No valid choices.'
    return random.choice(choices)
