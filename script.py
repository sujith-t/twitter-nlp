# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 21:18:25 2022

@author: Sujith T
"""

import snscrape.modules.twitter as sntwitter
import pandas as pd
import re
import requests
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

from datetime import datetime
from bs4 import BeautifulSoup

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
            tweets.append([tweet.id, tweet.date, tweet.user.username, tweet.content, news_url, None])
            count += 1
        
        print(count)
    headers = ['id', 'date', 'user', 'tweet', 'newsfeed_url', 'news_text']
    print("News items found : %d" % count)
    return pd.DataFrame(tweets, columns=headers)


"""
Scrape news from websites, extract and clean data
We only consider English text
"""


def extract_news(data_frame: pd.DataFrame):
    words = set(nltk.corpus.words.words())
    
    if not "newsfeed_url" in data_frame or not "news_text" in data_frame:
        print("Not a valid dataframe input, exiting...")
        return
    
    for i, row in data_frame.iterrows():

        if i < 3000:
            continue

        if i > 4000:
            print("max limit...")
            break
        
        try:
            response = requests.get(row['newsfeed_url'], timeout=60)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                data = ''.join(filter(visible, soup.findAll(text=True)))
                data = re.sub(r'[\t\r\n]', '', data)
                data = re.findall("[A-Za-z0-9:\.,!'\"\s\-]+", data)
                
                data = " ".join(w for w in data if w != ' ')
                data = " ".join(w for w in nltk.wordpunct_tokenize(data) if w.lower() in words or re.match(r"^[A-Z][A-Za-z]+$", w) or re.match(r"[0-9\"\.\']", w))
                data = re.sub(r'\ss\s', "'s ", data)
                data = re.sub(r'\st\s', "'t ", data)
                data = re.sub(r'\sve\s', "'ve ", data)
                data = re.sub(r'\sll\s', "'ll ", data)
                data = re.sub(r'\sd\s', "'d ", data)
                data = re.sub(r'\sy\s', "'y ", data)
                data = re.sub(r'\sm\s', "'m ", data)
                data = re.sub(r'\sam\s', "'am ", data)
                data = re.sub(r'\sre\s', "'re ", data)
                data = re.sub(r'\sn\s', "'n ", data)
                data = re.sub(r'\s\.', '.', data)
                data = re.sub(r'\s\,\s', ',', data)
                data = re.sub(r"\s\'", "'", data)
                data_frame.at[i,'news_text'] = data

        except:
            print("Connectivity error with news url: %s" % row['newsfeed_url'])
            continue
        
        print("%d %s" % (i, row['newsfeed_url']))

"""
Exclude texts from undergiven html elements
"""
      
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title', 'meta', 'Start', 'Post', 'img', 'svg']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

"""
Generate text statistics
"""
def generate_news_statistics(data_frame: pd.DataFrame):
    stats = []
    
    if not "newsfeed_url" in data_frame or not "news_text" in data_frame:
        print("Not a valid dataframe input, exiting...")
        return
    
    for i, row in data_frame.iterrows():
        news_text = str(row["news_text"])
        sentences = sent_tokenize(news_text)
        words = word_tokenize(news_text)
        unique_words = set(words)
        
        stats.append([row["id"], len(sentences), len(words), len(news_text), len(unique_words)])
        
    headers = ['id', 'sentences', 'words', 'length', 'unique_words']
    return pd.DataFrame(stats, columns=headers)