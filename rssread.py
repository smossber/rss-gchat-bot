#!/usr/bin/env python

import feedparser
import hashlib
import sys
import os
import json
import time

# We will generate a hash of the latest RSS post that we will save for matching later
# We should only notify if we haven't posted it already
# and we can't be keeping this in memory since we're running in a ephemeral pod.
# The hash is saved to the latest_post_hash on a persistent storage 
# specified with the env $RSS_DB_DIR

def check_env(env):
    env = str(env)
    try:
        os.environ[env]
    except KeyError:
        print "%s is not specified" % env
        sys.exit(1)
    if os.environ[env] == '':
        print "%s is empty" % env
        sys.exit(1)

for env_var in "RSS_DB_DIR","RSS_USER","RSS_PASS","RSS_URL","GCHAT_WEBHOOK":
    check_env(env_var)

# check that RSS_POLL_INTERVALL is castable to int
POLL_INTERVAL = 360

# check that RSS_DB_DIR exists
if not os.path.isdir(os.environ['RSS_DB_DIR']):
    print "Can't find RSS_DB_DIR %s" % os.environ['RSS_DB_DIR']
    sys.exit(1)

LAST_POST_FILE_NAME = os.environ['RSS_DB_DIR'] + "/" + "last_post.hash" 

# check if we have a last_post.hash file from before
last_post_link_exists = False
if os.path.isfile(LAST_POST_FILE_NAME):
    with open(LAST_POST_FILE_NAME, 'r') as f:
        try:
            data_json = json.load(f)
            last_post_link = data_json['last_post_link']
            last_post_link_exists = True
            print "Found previous latest post" 
            print str(data_json)
        except ValueError:
            last_post_link_exists = False
            print "No previous latest post found"

def notify(post):
    date = "(%d/%02d/%02d)" % (post.published_parsed.tm_year, post.published_parsed.tm_mon, post.published_parsed.tm_mday)
    print("post date: " + date)
    print("post title: " + post.title)
    print("post link: " + post.link)
    try:
        with open(LAST_POST_FILE_NAME, 'w') as f:
            f.write(json.dumps({"last_post_link": post.link}))
            last_post_link_exists = True
    except:
        raise

while True:
    url = os.environ['RSS_URL']
    feed = feedparser.parse(url)

    newest_post = feed.entries[0]
    if last_post_link_exists:
        if newest_post.link != last_post_link:
            notify(newest_post)
    else:
        notify(newest_post)
    print "No new posts, polling again in %s" % POLL_INTERVAL
    time.sleep(POLL_INTERVAL)
#print("post author: " + latest_post.author)
