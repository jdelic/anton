import commands
import re


@commands.register(re.compile("^((th)anks|(ch)eers|(n)ight|(y)o|(n)o|(bl)ess you) [^aeiou]*([a-z]+)$", re.IGNORECASE))
def thanks(callback, m):
    g = m.groups()
    for x in g[1:-1]:
        if x:
            break

    first, last = x, g[-1]

    return "%s%s" % (first, last)
