# LaterPay-specific modifications for Holly

## (Or, "How I turned Holly into Anton")

Anton currently runs on a [Heroku](http://www.heroku.com/) instance provided by Moorhen Solutions Ltd. (Kristian's company). This forces things to be a little more [12factor-y](http://www.12factor.net/) than Holly was originally written to be.

There is a fork of Holly at `laterpay/anton` on GitHub. This is forked from https://bitbucket.org/chrisporter/holly/. This exists for two reasons only:

1. So there is a "LaterPay backup"
2. For the `laterpay-heroku` branch

If you are working on the bot, for anything nonspecific, you should use https://bitbucket.org/chrisporter/holly/ as your source. 

If you are deploying the bot, you should adopt the following (slightly non-standard) procedure:

1. Ensure the `laterpay/anton` repo is up to date with changes in the upstream Holly repo
2. Checkout the `laterpay-heroku` branch (`git checkout laterpay-heroku`)
3. Merge any changes from `master` into `laterpay-heroku` (`git merge master`)
5. Push `laterpay-heroku` to `heroku/master` (`git push heroku laterpay-heroku:master`)

`laterpay-heroku` should be a **small** branch only for running-on-Heroku config. If you want to add LaterPay-specific features, do it on another branch.

## What does the `laterpay-heroku` branch contain?

1. A [Procfile](https://devcenter.heroku.com/articles/procfile) is included, for running on Heroku
2. Holly is designed so that you grab the code, and create your own `config.py`; Anton uses a `config.py` that gets its data from environment variables, in a 12factor / Heroku-compatible way.
3. Heroku dynos have an ephemeral filesystem; Holly's `learndb` module is currently implemented using a local `sqlite3` db; this will not work on Heroku so is disabled.

## Future notes

`learndb` is cool. Someone should probably refactor Holly to be more flexible in her backing db, or move Anton off Heroku and onto a LaterPay box.

Kristian (holly@doismellburning.co.uk) is maintaining Holly for the long term; contact him if you have any Holly issues/questions/opinions.
