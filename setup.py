from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

import time
_version = "1.0.dev%s" % int(time.time())
_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

pipsession = PipSession()
reqs_generator = parse_requirements("requirements.txt", session=pipsession)
reqs = [str(r.req) for r in reqs_generator]

test_reqs_generator = parse_requirements("requirements-test.txt", session=pipsession)
test_reqs = [str(r.req) for r in test_reqs_generator]

setup(
    name='irc.anton',
    data_files=[('',
        [
            'package.yaml',
            'requirements.txt',
            'requirements-test.txt',
            'Procfile',
            'README.md'
        ]
    ), ],
    scripts=[
        'scripts/bot.py',
        'scripts/run'
    ],
    version=_version,
    packages=_packages,
    install_requires=reqs,
    tests_require=test_reqs,
    test_suite="nose.collector",
)
