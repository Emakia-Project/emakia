import asyncio
import argparse
from twikit import Client, TooManyRequests
from datetime import datetime
from configparser import ConfigParser
from random import randint
import csv

# Set up argument parser
parser = argparse.ArgumentParser(description='Get tweets based on a query.')
parser.add_argument('query', type=str, help='The search query for retrieving tweets')
args = parser.parse_args()

# Use the passed argument as the QUERY
QUERY = args.query

config = ConfigParser()
config.read('config.ini')
username = config['X']['username']
email = config['X']['email']
password = config['X']['password']

print(f'{email} - email')  # Confirming email output

# Initialize client
client = Client('en-US')

async def get_tweets(tweets):
    if tweets is None:
        # Get tweets
        print(f'{datetime.now()} - Getting tweets...')
        tweets = await client.search_tweet(QUERY, product='Top')
        print(tweets)
    else:
        wait_time = randint(5, 10)
        print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds ...')
        await asyncio.sleep(wait_time)  # Non-blocking wait
        tweets = await tweets.next()

    return tweets

async def main():
    login_result = await client.login(auth_info_1=username, auth_info_2=email, password=password)
    print(f'{login_result} - login_result')

    tweet_count = 0
    MAX_TWEETS = 10
    tweets = None

    while tweet_count < MAX_TWEETS:
        try:
            print(f' in the while loop try')
            tweets = await get_tweets(tweets)
        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
            wait_time = (rate_limit_reset - datetime.now()).total_seconds()
            await asyncio.sleep(wait_time)
            continue

        if not tweets:
            print(f'{datetime.now()} - No more tweets found')
            break

        for tweet in tweets:
            tweet_count += 1
            tweet_data = [tweet_count, tweet.user.name, tweet.text, tweet.created_at, tweet.retweet_count, tweet.favorite_count]
            print(tweet_data)
            with open('tweets.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

        print(f'{datetime.now()} - Got {tweet_count} tweets')

    print(f'{datetime.now()} - Done! Got {tweet_count} tweets found')

asyncio.run(main())
