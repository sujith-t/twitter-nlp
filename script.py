# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 21:18:25 2022

@author: Sujith T
"""

import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
import requests

from datetime import date, datetime
from bs4 import BeautifulSoup
#from time import sleep

  
"""
Retrieve tweets, identify news items and return a dataframe
query - search key word string '"sports news"' is used in our case
num_tweets - upper limit on the number of tweets retrieved to identify news items
max_news - max news items required
"""
def find_tweets_with_news(from_date: datetime, to_date: datetime, query: str, num_tweets=20000, max_news=15000):
    tquery = "%s lang:en until:%s since:%s" % (query, to_date.strftime("%Y-%m-%d"), from_date.strftime("%Y-%m-%d"))
    tweets = []
    count = 0
    web_url_regex = "(https?://t\.co/([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)"
    
    for tweet in sntwitter.TwitterSearchScraper(tquery).get_items():
        if len(tweets) >= max_news or count >= num_tweets:
            break
        
        urls = re.findall(web_url_regex, tweet.content)
        news_url = ''
        for x in urls:
            news_url = x[0].strip()
            
        if len(news_url) > 0:
            tweets.append([tweet.id, tweet.date, tweet.user.username, tweet.content, news_url, ""])
            count +=1
            
    headers = ['id', 'date', 'user', 'tweet', 'newsfeed_url', 'news']                
    return pd.DataFrame(tweets, columns=headers)


"""
Scrape news from websites, extract and clean data
"""
def extract_news(data_frame: pd.DataFrame):
    
    for i, row in data_frame.iterrows():
        try:
            response = requests.get(row['newsfeed_url'], timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                data = ''.join(filter(visible, soup.findAll(text=True)))
                data = re.sub(r'[\t\r\n]', '', data)
                print(data)
                
        except requests.ConnectionError as e:
            print("Connectivity error with news url: %s" % row['newsfeed_url'])
            

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'meta', 'Start', 'Post', 'div']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True