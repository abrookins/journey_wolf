# Journey Wolf
This is a Twitter bot that reposts California Department of Fish and Game
updates on the GPS location of Gray Wolf OR-7, AKA "Journey.""

## About Journey
Journey is a badass. He has traveled on foot more than 2,000 miles
[(source)](http://www.latimes.com/news/local/la-me-wolf-california-20120303,0,6719205.story)
and was the first wild wolf in California since humans nearly wiped out wolves in
the early 1900s.

For more information on Journey, read [his web page](http://www.dfg.ca.gov/wildlife/nongame/wolf/OR7story.html).

## About this script
This is a Python script deployed on Heroku that runs once a day using Heroku's
scheduler addon. It retweets a couple of tweets about Journey and reposts a
status update on his location if one is available.