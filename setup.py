from distutils.core import setup
from setuptools import find_packages

import time
_version = "1.0.dev%s" % int(time.time())
_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

f = open("requirements.txt", "r")
requires = f.readlines()
requires = [r.strip() for r in requires]
f.close()

setup(
    name='irc.anton',
    data_files=[('', ['package.yaml', ]), ],
    scripts=[
        'scripts/holly.py',
        'scripts/run'
    ],
    version=_version,
    packages=_packages,
    install_requires=requires,
)
