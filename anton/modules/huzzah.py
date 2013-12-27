import random
from anton import commands
import re

answers = [
    'huzzah!',
    '\o/',
    'yo diggity!',
    'you rock!!!',
    'you are looking awesome today!',
    'black pepper?',
    'DOO EET! Seriously, do it.'
]

@commands.register(re.compile(r'^(huzzah.*|\\o|o/|\\o/)'))
def huzzah(callback, args):
    return answers[random.randint(0, len(answers) - 1)]

if __name__ == '__main__':
    import sys
    if re.match(r'^(huzzah.*|\\o|o/|\\o/)', sys.argv[1]):
        print huzzah(None, None)
    else:
        print "%s did not match regex" % sys.argv[1]
