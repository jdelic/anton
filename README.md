# Holly

Forked from https://bitbucket.org/chrisporter/holly/ because a bunch of us just plain fail at using Mercurial.

## Getting Started

```
$ pip install -r requirements.txt
$ cp config.py.example config.py
$ # Edit config.py
$ mkdir data
$ python holly.py
```

Note that OSX users may need to `CFLAGS="-I /opt/local/include -L /opt/local/lib" pip install gevent` to get gevent installed, as per http://stackoverflow.com/q/7630388/928098
