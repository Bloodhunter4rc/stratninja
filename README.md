# StratNinja
If you want to effortlessly track your dryruns on the strat.ninja website, here's a simple guide to get you started.

![image](https://github.com/Bloodhunter4rc/stratninja/assets/8630485/29b698a3-03a5-4937-85fd-7c3deda6aef5)


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

```
Additional to the token stratninja.post_stats accepts the following optional Arguments:
          private=("True"/"False") want to hide your dryruns on the page -> True
          strat("") = want to link your dryrun to a backtested strategy input the name of the strategy from the page here
          alternate_name("") = want a special display name set it here
```

- Restart / Startup your strategy

Your dryrun statistics will be posted on the strat.ninja page at the startup of your strategy and subsequently every 15 minutes if there is a change in closed trades. Please note that currently, only closed trades are considered.
Atleast 2 closed trades are needed before the statistics will be posted.

Your dryruns will be listed on https://strat.ninja/strats.php?tab=2 and in your personal profile on the page.

To access the data all your dryruns, visit http://strat.ninja/post.php?token=YOURSECRETTOKEN.
or http://strat.ninja/post.php?user=username (wont include private strat)

output looks like this:
```json
[
    {
        "strategy": "Synthesis_v5_log",
        "bot_name": "freqtrade",
        "exchange": "binance",
        "trading_mode": "TradingMode.SPOT",
        "timeframe": "5m",
        "stoploss": "-0.347",
        "trailing_stop": "False",
        "startup_candle_count": "999",
        "stake_currency": "USDT",
        "max_open_trades": "5",
        "stake_amount": "unlimited",
        "dry_run_wallet": "1000",
        "dry_run": "True",
        "trade_count": "48",
        "avg_duration": "0:29:00",
        "profit_closed_percent_mean": "-0.0443594",
        "profit_all_percent_sum": "-2.12925",
        "winning_trades": "16",
        "losing_trades": "32",
        "final_balance": "992.464",
        "winrate": "33.33",
        "profit_factor": "0.7390476680797265",
        "max_drawdown_abs": "13.1275",
        "drawdown_start": "2023-11-20 17:40:32+00:00",
        "drawdown_end": "2023-11-21 12:15:26+00:00",
        "dd_high_val": "0.455365",
        "dd_low_val": "-12.6721",
        "max_drawdown": "28.8285",
        "expectancy": "-0.157001",
        "expectancy_ratio": "-0.173968",
        "sortino_ratio": "-162.148",
        "sharpe_ratio": "-99.087",
        "calmar_ratio": "-1097.25",
        "cagr": "-0.936776",
        "trading_volume": "19645.2",
        "first_trade_timestamp": "1700500485352",
        "latest_trade_timestamp": "1700656527079",
        "user": "blood4rc",
        "userid": "210772580603265024",
        "uptime_d": "1",
        "updated": "2023-11-23 14:57:50"
    }
]
```
Limitations: Only closed trades are counted in the statistics.
