from __future__ import print_function

import random
from anton import commands

answers = [
    'Signs point to yes.',
    'Yes.',
    'Reply hazy, try again.',
    'Without a doubt.',
    'My sources say no.',
    'As I see it, yes.',
    'You may rely on it.',
    'Concentrate and ask again.',
    'Outlook not so good.',
    'It is decidedly so.',
    'Better not tell you now.',
    'Very doubtful.',
    'Yes - definitely.',
    'It is certain.',
    'Cannot predict now.',
    'Most likely.',
    'Ask again later.',
    'My reply is no.',
    'Outlook good.',
    "Don't count on it.",
]


@commands.register('!8ball')
def eightball(callback, *args):
    return random.choice(answers)

if __name__ == '__main__':
    eightball(print, '!8ball')
    eightball(print, '!8ball')
    eightball(print, '!8ball')
