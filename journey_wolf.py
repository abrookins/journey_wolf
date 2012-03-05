"""
journey_wolf: A script that updates Twitter with the current location of
Journey Wolf, AKA OR-7.

Copyright (c) 2012 Andrew Brookins. All Rights Reserved.
"""

#!/usr/bin/env python

import os
import requests
import random
import sys
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
    search_string = os.environ.get('SEARCH_STRING')
    retweet_limit = int(os.environ.get('RETWEET_LIMIT'))
    api = get_twitter_api()
    user = api.me()
    home_tweets = [t.text for t in api.home_timeline()]
    tweets_about_journey = api.search(search_string)

    random.shuffle(tweets_about_journey)
    num_tweeted = 0

    for tweet in tweets_about_journey:
        # Exclude retweets, tweets we've already retweeted and our own tweets
        if tweet.text.startswith('RT ') \
                or 'RT @%s: %s' % (tweet.from_user, tweet.text) in home_tweets \
                or tweet.from_user_id == user.id:
            continue

        try:
            api.retweet(tweet.id)
            num_tweeted += 1
        except tweepy.error.TweepError as e:
            print >> sys.stderr, "Error, skipping retweet: %s" % e

        print "Retweeted: %s" % tweet.text

        if num_tweeted == retweet_limit:
            return


def update_status():
    """
    Parse the latest status of Journey Wolf/OR-7 from the The California
    Department of Fish and Game's OR-7 status page and update a Twitter account
    with the content of the status.
    """
    latest_title, latest_link = get_latest_cfg_update()
    api = get_twitter_api()

    # Ignore any status that we've already tweeted.
    possible_duplicates = [t.text[:len(latest_title)]
                           for t in api.home_timeline()]

    if latest_title not in possible_duplicates:
        new_tweet = u'%s %s' % (latest_title, latest_link)

        try:
            api.update_status()
        except tweepy.error.TweepError as e:
            print >> sys.stderr, "Error, could not tweet: %s" % e

        print "Tweeted: %s" % new_tweet


if __name__ == "__main__":
    print "Running..."
    update_status()
    retweet()
    print "Done!"