# Anton, the LaterPay IRC bot that supports webhooks

Anton is an instance of [Holly](https://bitbucket.org/chrisporter/holly/).

Anton currently runs on `anton.laterpay.net`, a VM on dev.laterpay.net.

There is a fork of Holly at `laterpay/anton` on GitHub. This is forked from https://bitbucket.org/chrisporter/holly/. This exists for two reasons only:

1. So there is a "LaterPay backup"
2. For this README.

If you are working on the bot, for anything nonspecific, you should use https://bitbucket.org/chrisporter/holly/ as your source. If you are adding anything LaterPay-specific to the bot, see if you can make it generic.

## Upgrading / configuring / tweaking Anton

In production, Anton runs via supervisor (or any other watcher process). On it's VM (anton.laterpay.net), it lives in /srv/anton. Anton is mostly configured through environment variables set in its supervisord config.

Here is an example config:

    [program:anton]
    user=anton
    command=/srv/anton/.env/bin/python /srv/anton/holly.py
    autostart=true
    autorestart=true
    environment=IRC_SERVER_HOST="YOUR.IRCSER.VER",
        IRC_SERVER_PORT="6667",
        PORT="80",
        JENKINS_CHANNEL="#laterpay-ci",
        GITHUB_AUTH_TOKEN="[create an auth token]"

On anton.laterpay.net, this config lives in /etc/supervisor/conf.d, but as you can see, Anton has its own virtualenv in `.env`, so it could also run its own copy of supervisor.

## How do I create a GitHub auth token?

By sending a HTTP POST to GitHub via curl. The following example is adapted from the [original docs](https://help.github.com/articles/creating-an-oauth-token-for-command-line-use).

    curl -u 'laterpay-jenkins' -d '{"scopes":["repo"],"note":"OAuth Token for LaterPay Bots (authorized by [YOUREMAILADDRESS])"}' https://api.github.com/authorizations

This will return a JSON object that has your GitHub auth token. The `note` will show up in your GitHub user account. As in the above example, LaterPay has a dedicated jenkins user on GitHub that we use for this kind of thing.

## What webhooks does Anton support?

Anton supports GitHub post requests and Jenkins callbacks. If you move anton, make sure you also change the webhooks on jenkins.laterpay.net.

## What did the `laterpay-heroku` branch contain?

Before Anton ran on `perigee` and later in its own VM, it ran on Heroku, which required a few modifications that never made it upstream; these lived in `laterpay-heroku`. Now the branch exists solely for this README.

## Future notes

Kristian (holly@doismellburning.co.uk) is maintaining Holly for the long term; contact him if you have any Holly issues/questions/opinions.
