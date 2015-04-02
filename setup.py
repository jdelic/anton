from setuptools import setup, find_packages
from distutils.command.install import INSTALL_SCHEMES
from pip.req import parse_requirements

import time
_version = "1.0.dev%s" % int(time.time())
_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

reqs_generator = parse_requirements("requirements.txt")
reqs = [str(r.req) for r in reqs_generator]

setup(
    name='irc.anton',
    data_files=[('', ['package.yaml', 'requirements.txt', 'Procfile', 'README.md']), ],
    scripts=[
        'scripts/bot.py',
        'scripts/run'
    ],
    version=_version,
    packages=_packages,
    install_requires=reqs,
    test_suite="anton.tests",
)
