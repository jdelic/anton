# Anton

Anton is an instance of [Holly](https://bitbucket.org/chrisporter/holly/).

Anton currently runs on `perigee`, @carlio's server that also hosts the ircd.

There is a fork of Holly at `laterpay/anton` on GitHub. This is forked from https://bitbucket.org/chrisporter/holly/. This exists for two reasons only:

1. So there is a "LaterPay backup"
2. For this README.

If you are working on the bot, for anything nonspecific, you should use https://bitbucket.org/chrisporter/holly/ as your source. If you are adding anything LaterPay-specific to the bot, see if you can make it generic.

## Upgrading / configuring / tweaking Anton

Anton lives in a git repo on `perigee.carlcrowder.com` in `/srv/anton`. (Anton should probably be moved to a LaterPay server...)

He runs via `supervisor` (see `/etc/supervisor/conf.d/anton.conf`) and has an `httpd` that `nginx` proxies to (see `/etc/nginx/sites-available/anton`).

## What did the `laterpay-heroku` branch contain?

Before Anton ran on `perigee`, it ran on Heroku, which required a few modifications that never made it upstream; these lived in `laterpay-heroku`. Now the branch exists solely for this README.

## Future notes

Kristian (holly@doismellburning.co.uk) is maintaining Holly for the long term; contact him if you have any Holly issues/questions/opinions.
