#!/usr/bin/env python3
# A simple script to print some messages.
import os
import sys
import time
import configparser
from telethon import TelegramClient, events, utils
import time
from templateTextParser import templateTextParser
import pandas as pd
from Class_API_binance import API_Binance

def get_env(name, message, cast=str):
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)


session = os.environ.get('TG_SESSION', 'printer')
# api_id = get_env('TG_API_ID', 'Enter your API ID: ', int)
# api_hash = get_env('TG_API_HASH', 'Enter your API hash: ')+886921582871


'''
Initial SETUP
'''
pickleFileName = "transactionRecord.pickle"

config = configparser.ConfigParser()
config.read('login_info.ini')
api_id=config["Telegram"]["api_id"]
api_hash=config["Telegram"]["api_hash"]

proxy = None  # https://github.com/Anorov/PySocks

# Create and start the client so we can make requests (we don't here)
client = TelegramClient(session, api_id, api_hash, proxy=proxy).start()


# `pattern` is a regex, see https://docs.python.org/3/library/re.html
# Use https://regexone.com/ if you want a more interactive way of learning.
#
# "(?i)" makes it case-insensitive, and | separates "options".
@client.on(events.NewMessage(pattern=r'\S*'))
async def handler(event):
    sender = await event.get_sender()
    name = utils.get_display_name(sender)
    print(name, 'said', event.text, '!')



    receivedText = '{\n"Symbol": "ADA/USDT 4H BINANCE",\n"Side": "BUY",\n"Price": 1.073,\n"StopLoss": "1.011",\n"Timestamp": "2022-01-29 16:00:00",\n"Translation": "ADA/USDT 建議買入1.073, 止損1.04",\n"Disclaimer": "嚴格執行停損，本分析不擔負任何損失賠償責任。"}'
    template = '{\n"Symbol": "{{Symbol}}",\n"Side": "{{Side}}",\n"Price": {{Price}},\n"StopLoss": "{{StopLoss}}",\n"Timestamp": "{{Timestamp}}","Translation": "xxxxxx",\n"Disclaimer": "嚴格執行停損，本分析不擔負任何損失賠償責任。"}'


    parserResult = templateTextParser(event.text, template)  #Return : { Symbol , Side ,Price,StopLoss,Timestamp}
    ifTargetString = True
    for i in parserResult.values():
        if i == "":
            # this is not target string
            ifTargetString = False
            break

    if ifTargetString:
        parserResult['Symbol'] = parserResult['Symbol'].split(" ")[0].replace("/", "")

        # MICK_TODO :
        # calc the quality of transaction
        binance_handler = API_Binance()
        binance_handler.execute_order(parserResult,15,'TEST')


        df = pd.DataFrame([parserResult])
        print(df)
        if os.path.isfile(pickleFileName):
            readDF = pd.read_pickle(pickleFileName)
            res = pd.concat([readDF, df], axis=0, ignore_index=True)
            res.to_pickle(pickleFileName)
        else:
            df.to_pickle(pickleFileName)

try:
    print('(Press Ctrl+C to stop this)')
    client.run_until_disconnected()
finally:
    client.disconnect()

# Note: We used try/finally to show it can be done this way, but using:
#
#   with client:
#       client.run_until_disconnected()
#
# is almost always a better idea.