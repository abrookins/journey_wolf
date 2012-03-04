"""
journey_wolf: A script that updates Twitter with the current location of
Journey Wolf, AKA OR-7.

Copyright (c) 2012 Andrew Brookins. All Rights Reserved.
"""

#!/usr/bin/env python

import os
import requests
import random
import tweepy

from BeautifulSoup import BeautifulSoup


def get_twitter_api():
    """ Authenticate with Twitter and return a `tweety.API` instance. """
    twitter_consumer_key = os.environ.get('CONSUMER_KEY')
    twitter_consumer_secret = os.environ.get('CONSUMER_SECRET')
    twitter_access_token = os.environ.get('ACCESS_TOKEN')
    twitter_access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

    auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
    auth.set_access_token(twitter_access_token, twitter_access_token_secret)
    return tweepy.API(auth)


def get_soup(url):
    """ Return a `BeautifulSoup` object parsed from `url`. """
    return BeautifulSoup(
        requests.get(url).text,
        convertEntities=BeautifulSoup.HTML_ENTITIES)


def get_latest_cfg_update():
    """
    Get the latest Journey Wolf status update from the California Department of
    Fish and Game's web site.
    """
    # The California Department of Fish and Game's OR-7 status page.
    cali_fish_and_game_status_page = os.environ.get('FISH_AND_GAME_STATUS_PAGE')
    content = get_soup(cali_fish_and_game_status_page)
    items = content.findAll('div', {'class': 'postcontent'})

    # This is an <h2> with an embedded link.
    latest_update = items[0].first() 
    # Get the content of the href.
    link = latest_update.find('a').attrs[0][1]
    title = latest_update.text
    return title, link


def retweet():
    """ Retweet some recent tweets about OR-7/Journey Wolf. """
    retweet_limit = os.environ.get('RETWEET_LIMIT')
    api = get_twitter_api()
    home_tweets = [t.text for t in api.home_timeline()]
    tweets_about_journey = api.search('Journey Wolf')
    to_retweet = []

    # Exclude retweets from the list of potential candidates.
    possible_rts = [t for t in tweets_about_journey
                    if not t.text.startswith('RT ')]

    # Exclude tweets we've already retweeted.
    candidates = [t for t in possible_rts
                  if 'RT %s' % t.text not in home_tweets]

    if len(candidates) == 1:
        to_retweet = candidates
    elif len(candidates) >= retweet_limit:
        random.shuffle(candidates)
        to_retweet = candidates[:retweet_limit]

    for t in to_retweet:
        api.retweet(t.id)


def update_status():
    """
    Parse the latest status of Journey Wolf/OR-7 from the The California
    Department of Fish and Game's OR-7 status page and update a Twitter account
    with the content of the status.
    """
    latest_title, latest_link = get_latest_cfg_update()
    api = get_twitter_api()

    # Ignore a status that we've already tweeted.
    possible_duplicates = [t.text[:len(latest_title)]
                           for t in api.home_timeline()]

    if latest_title not in possible_duplicates:
        new_tweet = u'%s %s' % (latest_title, latest_link)
        api.update_status(new_tweet)


if __name__ == "__main__":
    update_status()
    retweet()
