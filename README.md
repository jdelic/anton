# Anton, the LaterPay IRC bot

Anton is an fork of [Holly](https://bitbucket.org/chrisporter/holly/).

Anton currently runs on `anton.laterpay.net`, which is hosted on `irc.laterpay.net`.

At this point Anton has diverged a lot from Holly, however some of our changes might make it upstream at some point :).

## Upgrading / configuring / tweaking Anton

In production, Anton runs via DJB supervise (or any other watcher process). On LaterPay servers it's deployed as a RPM
and subsequently run from its service directory `/opt/lp-supervise/run` which loads Anton's `run` script.
Anton is configured through environment variables set in its supervisord/daemontools config.

Here is an example config:

    [program:anton]
    user=anton
    command=/srv/anton/.env/bin/python /srv/anton/holly.py
    autostart=true
    autorestart=true
    environment=IRC_SERVER="YOUR.IRCSER.VER"
        IRC_PORT="8080",
        HTTP_BINDADRESS="127.0.0.1",
        HTTP_PORT="8000",
        JENKINS_CHANNEL="#laterpay-ci",
        GITHUB_AUTH_TOKEN="[create an auth token]"
        ...

## List of Anton configuration variables

Variable | Description
--- | ---
WORKING_DIR | "."
IRC_SERVER | The hostname or IP address of the IRC server which Anton should connect to. (Default: 127.0.0.1)
IRC_PORT | The port that Anton should connect to. (Default: 6667)
HTTP_BINDADDRESS | The IP address that Anton should bind its webhook listener to. (Default: 127.0.0.1)
HTTP_PORT | The port that Anton should listen on for HTTP webhooks. (Default: 8000)
HTTP_ROOT | A path prefix for HTTP handlers. There isn't much reason to ever change this. (Default: "/bot")
BOT_USERNAME | The bot's IRC username (Default: "anton")
BOT_REALNAME | The bot's IRC real name (Default: "anton")
BOT_NICKNAME | The bot's IRC nickname (Default: "antonia")
BOT_CHANNELS | A comma-separated list of channels the bot should connect to. (Default: "#twilightzone")
SENTRY_DSN | An optional DSN that will connect Anton's error handling to a Sentry instance

## List of Anton module configuration variables

Variable | Description
--- | ---
JENKINS_CHANNEL | The channel where Anton posts webhook calls made to the Jenkins CI handler (Default: #twilightzone)
TICKET_PROVIDER | If you want to connect Anton to a ticket tracker, it currently supports JIRA and GitHub tickets. Set this to either `anton.modules.tickets.jira.JiraTicketProvider` or `anton.modules.tickets.github.GitHubTicketProvider` accordingly.
GITHUB_CHANNEL  | The channel where Anton posts webhook calls made to the GitHub handler (Default: #twilightzone)
GITHUB_AUTH_TOKEN | A GitHub OAuth2 token for Anton (see below for docs on how to create this)
GITHUB_DEFAULT_ORGANIZATION | The default organization to search (Default: 'laterpay')
GITHUB_DEFAULT_REPO | The default repository name to search (Default: 'laterpay')
JIRA_URL | A HTTP(S) URL pointing to your organization's JIRA (Default: "https://laterpay.atlassian.net")
JIRA_AUTH_TOKEN | A JIRA OAuth1 token (see below for docs on how to create this)
JIRA_AUTH_SECRET | A JIRA OAuth1 secret key (see below for docs on how to create this)
JIRA_AUTH_ID | The JIRA application link ID (Default: "anton")
JIRA_AUTH_PRIVATEKEY | A RSA private key, starting with "-----BEGIN RSA PRIVATE KEY-----" registered with JIRA.

## How do I create a GitHub auth token?

By sending a HTTP POST to GitHub via curl. The following example is adapted from the
[original docs](https://help.github.com/articles/creating-an-oauth-token-for-command-line-use).

    curl -u 'laterpay-jenkins' -d '{"scopes":["repo"],"note":"OAuth Token for LaterPay Bots (authorized by [YOUREMAILADDRESS])"}' https://api.github.com/authorizations

This will return a JSON object that has your GitHub auth token. The `note` will show up in your GitHub user account.
As in the above example, LaterPay has a dedicated jenkins user on GitHub that we use for this kind of thing.

## How do I connect Anton to JIRA?

JIRA has the most convoluted setup path for OAuth imaginable. That said: Here is how you authorize Anton on JIRA:

First, use `openssl` to generate a RSA key pair:

    openssl genrsa -out anton.secretkey 2048
    openssl rsa -pubout -in anton.secretkey

Now follow these steps:

  * Log into JIRA as an Administrator
  * Go to Settings -> Add-Ons -> Application Links
  * Enter the URL of your Anton bot (or any URL, really) and click "Create New Link"
  * Click "Continue"
  * Enter an application name like "Anton IRC bot" and select "Generic Application", leave the other fields empty.
  * Click "Continue"
  * Now click "Edit" next to the "Anton IRC bot" entry
  * Click on "Incoming Authentication"
  * Set consumer key to the value of `JIRA_AUTH_ID` in Anton's config (for example: "anton")
  * Set consumer name to "Anton IRC bot"
  * Paste the public key *without* the `-----BEGIN PUBLIC KEY-----` and `-----END PUBLIC KEY-----` lines into the
    "Public Key" field
  * Click "Save"
  * Log out of JIRA!

You will need to put the private key either into `config.py` or into the `JIRA_AUTH_PRIVATEKEY` environment variable.
In this case, it's good to know that DJB `envdir` will replace ASCII 0 with newline characters when reading files
in an envdir.

Finally it's time to authorize Anton. Do *NOT* use an JIRA administrator account for this (because: security!). Inside
Anton's virtualenv run this:

    bin/jirashell -s [your JIRA server URL] -od -ck [JIRA_AUTH_ID] -k /path/to/anton.secretkey -pt

  * If, like me, you don't have browsers on your development VMs, you'll need to patch
    `lib/python2.7/site-packages/tools/jirashell.py` line 52 to output `auth_url`! I submitted a pull request for
    that.
  * This command will launch a browser and go to your JIRA server. This is why you logged out before. Now log in with an
    *unprivileged* account (for example a member of the "Developers" group, which has access to all tickets which you
    want the bot to have access to).
  * Authorize the application.
  * `jirashell` will output a OAuth1 token and secret. You need to put these into `JIRA_AUTH_TOKEN` and
    `JIRA_AUTH_SECRET`.

Finally... you're done.

## What webhooks does Anton support?

Anton supports GitHub post requests and Jenkins callbacks.

## How do I develop with Anton?

Clone it, create a virtualenv and pip install it:

    git clone https://github.com/laterpay/anton.git anton
    virtualenv .env
    .env/bin/pip install -e anton

## Future notes

Kristian (holly@doismellburning.co.uk) is maintaining Holly for the long term; contact him if you have any Holly
issues/questions/opinions. LaterPay's fork was primarily architected by @jdelic.
