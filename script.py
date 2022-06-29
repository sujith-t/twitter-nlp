# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 21:18:25 2022

@author: sujith
"""

import snscrape.modules.twitter as sntwitter
from datetime import date, datetime
import pandas as pd

# dynamically get sports related 10,000 tweets from last year
today = date.today()
from_date = datetime(today.year - 1, today.month, today.day)
query = "(sports) lang:en until:%s since:%s" % (today.strftime("%Y-%m-%d"), from_date.strftime("%Y-%m-%d"))
limit = 5
tweets = []

for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    if len(tweets) == limit:
        break
    tweet.
    tweets.append([tweet.date, tweet.user.username, tweet.content])
    
dt = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet'])