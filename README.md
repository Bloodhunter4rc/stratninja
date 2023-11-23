# StratNinja
If you want to effortlessly track your dryruns on the strat.ninja website, here's a simple guide to get you started.

# Prerequisites
Ensure you have at least one strategy uploaded on strat.ninja.

# How to use?

Obtain your token from the strat.ninja website by navigating to Upload -> Profile after logging in with Discord.

![s1](https://github.com/Bloodhunter4rc/stratninja/assets/8630485/6606075c-5b1f-494f-b6dc-2988a6d16762)

(Note: Currently, the token requires at least one uploaded strategy to function.)

Place the [stratninja.py](https://github.com/Bloodhunter4rc/stratninja/blob/main/stratninja.py) file into your strategies directory where you will run your strategy.

In your strategy file, add the following import at the top:

```python
import stratninja
```
Insert the following function into your strategy file, replacing "YOURSECRETTOKEN" with your obtained token:

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

Your dryrun statistics will be posted on the strat.ninja page at the startup of your strategy and subsequently every 15 minutes if there is a change in closed trades. Please note that currently, only closed trades are considered.
Atleast 2 closed trades are needed before the statistics will be posted.

Your dryruns will be listed on https://strat.ninja/dry.php and in your personal profile on the page.

To access all your dryruns, visit http://strat.ninja/post.php?token=YOURSECRETTOKEN.

Limitations: Only closed trades are counted in the statistics.
