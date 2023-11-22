# stratninja
Used to post your dryruns to the strat.ninja Website, easy way to keep track of your dryruns.

# Prerequisites
Atleast 1 uploaded Strategy on strat.ninja

# How to use?

Receive the token from the strat.ninja website in Upload->Profile after being logged in with discord.

![s1](https://github.com/Bloodhunter4rc/stratninja/assets/8630485/6606075c-5b1f-494f-b6dc-2988a6d16762)

(Currently it is set that you need to have uploaded atleast 1 strategy for the token to work)

Place the stratninja.py file into your strategies directory where you will run your strategy.

Inside your strategy add the stratninja import on top of the file

```python
import stratninja
```
Add the following function to your strategy AND insert your token into YOURSECRETTOKEN:

```python
    def bot_loop_start(self, **kwargs) -> None:
        """
        Called at the start of the bot iteration (one loop).
        Might be used to perform pair-independent tasks
        (e.g. gather some remote resource for comparison)
        :param **kwargs: Ensure to keep this here so updates to this won't break your strategy.
        """
        stratninja.post_stats(self.config, token="YOURSECRETTOKEN")
```

- Restart / Startup your strategy

Your dryrun statistics will be posted to the page at startup of your strategy and after that every 15 minutes if there is a change on closed trades.
Currently this will only handle closed Trades.

It will be listed on:
https://strat.ninja/dry.php
And also in your personal profile on the page.

You can receive all your dryruns by visiting:
http://strat.ninja/post.php?token=YOURSECRETTOKEN

Limitations:
Only closed trades are counted.
