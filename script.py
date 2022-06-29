# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 21:18:25 2022

@author: sujith
"""

import snscrape.modules.twitter as sntwitter
from datetime import date, datetime
import pandas as pd
import re

web_url_regex = "((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)"

# dynamically get sports related 10,000 tweets from last year
limit = 5
tweets = []
today = date.today()
from_date = datetime(today.year - 1, today.month, today.day)
query = "\"sports news\" lang:en until:%s since:%s" % (today.strftime("%Y-%m-%d"), from_date.strftime("%Y-%m-%d"))

for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    if len(tweets) == limit:
        break
    
    urls = re.findall(web_url_regex, tweet.content)
    news_url = ''
    for x in urls:
        news_url = x[0].strip()
        
    #print(vars(tweet))
    if len(news_url) > 0:
        tweets.append([tweet.date, tweet.user.username, tweet.content, news_url])
    
dt = pd.DataFrame(tweets, columns=['Date', 'User', 'Tweet', 'NewsFeed_URL'])