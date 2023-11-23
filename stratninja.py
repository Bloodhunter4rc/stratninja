from datetime import datetime, timedelta, timezone
import json
import requests
import logging as logger
from freqtrade.data.btanalysis import load_trades_from_db
from freqtrade.data.metrics import calculate_expectancy, calculate_max_drawdown, calculate_sortino, calculate_sharpe, calculate_calmar, calculate_cagr
import time

logger = logger.getLogger()

custom_info = {'latest_update': datetime(2000, 1, 1)}
total_trades = 0
firstrun = True

def calculate_average(lst):
    if not lst:
        return None  # Handle the case where the list is empty to avoid division by zero

    total = sum(lst)
    average = total / len(lst)
    return average

def post_stats(config, token="", private="False", strat="", alternate_name=""):
   """
   args:
          token = your token from strat.ninja/upload on your profile page.
          private = want to hide your dryruns on the page -> True
          strat = want to link your dryrun to a backtested strategy, provide the name of the strategy here
          alternate_name = want a special display name set it here
   """
   global custom_info
   global total_trades
   global firstrun

   start_time = time.time()  # Record the start time

   if config['runmode'].value in ('live', 'dry_run'):
      dateTime = datetime.now()
      timeSinceLatestUpdate = dateTime - custom_info['latest_update']

      if timeSinceLatestUpdate > timedelta(minutes=15):
         tradesx = load_trades_from_db(config['db_url'])
         trades = tradesx.to_json(orient='records', lines=True)
         custom_info['latest_update'] = dateTime
      else:
         return False
   else:
      return False

   php_url = "https://strat.ninja/post.php?token=" + str(token)

   wins = 0
   losses = 0
   total_profit = 0

   strategy = "Temp"
   exchange = "Binance"
   stake_currency = ""


   strategy = config['strategy']
   stake_currency = config['stake_currency']
   timeframe = ""

   if config['timeframe']:
      timeframe = config['timeframe']

   exchange = config['exchange']['name']
   winning_profit = 0
   losing_profit = 0
   winrate = 0

   trade_duration_list = []
   profit_mean_list = []
   total_volume_list = []

   latest_timestamp = 0
   first_trade_timestamp = 0
   profit_mean = 0
   total_volume = 0

   json_data_lines = trades.strip().split('\n')

   dry_run_wallet = config.get('dry_run_wallet', "1000")
   final_balance = dry_run_wallet

   if len(json_data_lines) <= 1:
      total_trades = 0
      logger.info("Skip Update - StratNinja - Less than 2 Trades.")
      return False

   for xx in json_data_lines:
      json_data = json.loads(xx)
      pair = json_data["pair"]
      stake_amount = json_data["stake_amount"]
      profit_abs = json_data["profit_abs"]
      open_timestamp = json_data["open_timestamp"]

      if (json_data['profit_ratio']):
         profit_mean_list.append(json_data['profit_ratio'])

      if (json_data['stake_amount']):
         total_volume_list.append(json_data['stake_amount'])

      if str(first_trade_timestamp) == "0":
         first_trade_timestamp = open_timestamp
      elif int(open_timestamp) < int(first_trade_timestamp):
         first_trade_timestamp = open_timestamp

      if int(open_timestamp) > int(latest_timestamp):
         latest_timestamp = open_timestamp

      if profit_abs == None:
         profit_abs = 0
      else:
         final_balance = final_balance + profit_abs

      if json_data["close_date"]:
         close_timestamp = json_data["close_date"] / 1000.0
         open_timestamp = json_data["open_date"] / 1000.0

         close_date = datetime.utcfromtimestamp(close_timestamp)
         open_date = datetime.utcfromtimestamp(open_timestamp)

         trade_duration = (close_date - open_date).total_seconds()

      profit_ratio = json_data["profit_ratio"]

      if profit_ratio == None:
         profit_ratio = 0

      if float(profit_abs) > 0:
         winning_profit = winning_profit + float(profit_abs)
      if float(profit_abs) < 0:
         losing_profit = losing_profit + float(profit_abs)


      if trade_duration != None:
         trade_duration_list.append(trade_duration)

      if float(profit_ratio) > 0:
         wins+=1
      else:
         losses+=1

   current_total_trades = int(wins) + int(losses)

   if current_total_trades == total_trades:
      logger.info("Skip Update - StratNinja - No more Trades since last update.")
      return False
   else:
      total_trades = current_total_trades

   if profit_mean_list:
      profit_mean = (sum(profit_mean_list) / len(profit_mean_list)) * 100
      profit_sum = sum(profit_mean_list) * 100

   if total_volume_list:
      total_volume = sum(total_volume_list) * 2

   total_losses = abs(losing_profit)
   profit_factor = winning_profit / abs(losing_profit) if losing_profit else float('inf')

   winrate = (wins / total_trades) * 100
   winrate = "{:.2f}".format(winrate)

   total_trades = total_trades

   num = float(len(trade_duration_list) or 1)

   avg_trade_duration = str(timedelta(seconds=sum(trade_duration_list) / num)).split('.')[0]

   try:
      expectancy,expectancy_ratio = calculate_expectancy(tradesx)
   except TypeError as e:
      expectancy, expectancy_ratio = 0, 0

   try:
      (max_drawdown_abs, drawdown_start, drawdown_end, dd_high_val, dd_low_val, max_drawdown) = calculate_max_drawdown(tradesx)
   except:
      max_drawdown_abs = 0
      drawdown_start = 0
      drawdown_end = 0
      dd_high_val = 0
      dd_low_val = 0
      max_drawdown = 0

   min_date = datetime.utcfromtimestamp(first_trade_timestamp / 1000.0)
   max_date = datetime.utcfromtimestamp(latest_timestamp / 1000.0)

   try:
      sortino_ratio = calculate_sortino(tradesx, min_date, max_date, dry_run_wallet)
   except TypeError as e:
      sortino_ratio = 0

   try:
      sharpe_ratio = calculate_sharpe(tradesx, min_date, max_date, dry_run_wallet)
   except TypeError as e:
      sharpe_ratio = 0

   try:
      calmar_ratio = calculate_calmar(tradesx, min_date, max_date, dry_run_wallet)
   except TypeError as e:
      calmar_ratio = 0

   dayspassed = (max_date - min_date).days

   if dayspassed:
      cagr = calculate_cagr(dayspassed, dry_run_wallet, final_balance)
   else:
      cagr = 0

   calmar_ratio = str(calmar_ratio)

   # Sample data to be sent in the POST request
   data_to_send = {
      "strategy": config['strategy'],
      "exchange": config['exchange']['name'],
      "winning_trades": wins,
      "losing_trades": losses,
      "final_balance": str(final_balance),
      "profit_all_percent_sum": winning_profit,
      "stake_currency": config['stake_currency'],
      "timeframe": config['timeframe'] if config['timeframe'] else "",
      "stoploss": config.get('stoploss', "0"),
      "trailing_stop": str(config.get('trailing_stop', "False")),
      "trailing_stop_positive": config.get('trailing_stop_positive', "0"),
      "trailing_stop_positive_offset": config.get('trailing_stop_positive_offset', "0"),
      "trailing_only_offset_is_reached": str(config.get('trailing_only_offset_is_reached', "False")),
      "startup_candle_count": config.get('startup_candle_count', "0"),
      "exit_profit_only": config.get('exit_profit_only', "False"),
      "trade_count": total_trades,
      "profit_factor": str(profit_factor),
      "max_drawdown_abs" : str(max_drawdown_abs),
      "drawdown_start" : str(drawdown_start),
      "drawdown_end" : str(drawdown_end),
      "dd_high_val" : str(dd_high_val),
      "dd_low_val" : str(dd_low_val),
      "max_drawdown": str(max_drawdown),
      "winrate": winrate,
      "expectancy": str(expectancy),
      "expectancy_ratio": str(expectancy_ratio),
      "sortino_ratio": str(sortino_ratio),
      "sharpe_ratio": str(sharpe_ratio),
      "calmar_ratio": str(calmar_ratio),
      "cagr": str(cagr),
      "avg_duration": avg_trade_duration,
      "latest_trade_timestamp": str(latest_timestamp),
      "first_trade_timestamp": str(first_trade_timestamp),
      "trading_volume": str(total_volume),
      "profit_closed_percent_mean": str(profit_mean),
      "profit_all_percent_sum": str(profit_sum),
      "max_open_trades": config.get('max_open_trades', "inf"),
      "stake_amount": config.get('stake_amount', "inf"),
      "dry_run": str(config.get('dry_run', "true")),
      "bot_name": str(config.get('bot_name', "freqtrade")),
      "dry_run_wallet": str(dry_run_wallet),
      "trading_mode": str(config.get('trading_mode', "spot")),
      "uptime_d": str(dayspassed),
      "private": private,
      "strat": strat,
      "alternate_name": alternate_name
    }

   if not firstrun:
      keys_to_remove = ["strat", "dry_run_wallet", "bot_name", "dry_run", "stake_amount", "max_open_trades", "stoploss", "trailing_stop", "trailing_stop_positive", "trailing_stop_positive", "trailing_only_offset_is_reached", "startup_candle_count", "exit_profit_only"]
      data_to_send = {key: value for key, value in data_to_send.items() if key not in keys_to_remove}

   if data_to_send["trailing_stop"] == "False":
      keys_to_remove_trailing_stop = ["trailing_stop_positive", "trailing_stop_positive_offset", "trailing_only_offset_is_reached"]
      data_to_send = {key: value for key, value in data_to_send.items() if key not in keys_to_remove_trailing_stop}

   data_to_send = {key: value for key, value in data_to_send.items() if value is not None}

   json_data_to_send = json.dumps(data_to_send)

   # Set the headers for the POST request
   headers = {
       "Content-Type": "application/json"
   }

   # Send the POST request
   try:
      response = requests.post(php_url, data=json_data_to_send, headers=headers)
   except Exception as e:
      logger.info("Error - StratNinja - Unable to Post Statistics! - " + str(e) )
      return False

   end_time = time.time()  # Record the end time
   elapsed_time = round(end_time - start_time,2)  # Calculate the elapsed time

   # Check the response status
   if response.status_code == 200:
      firstrun = False
      logger.info(f"Updated - StratNinja - Request successful, took {elapsed_time} seconds to execute!")
      #logger.info("Response content:", response.text)
   else:
      logger.info(f"Request failed with status code {response.status_code}")
      logger.info("Response content:", response.text)

   return True
