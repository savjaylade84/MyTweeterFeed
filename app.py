from flask import Flask, render_template,request
from dotenv import load_dotenv
import os
import tweepy

# Load environment variables
load_dotenv()

# Get Twitter API credentials
CONSUMER_KEY = os.getenv('CONSUMER_KEY')
CONSUMER_SECRET = os.getenv('CONSUMER_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
ACCESS_KEY = os.getenv('ACCESS_KEY')
ACCESS_SECRET = os.getenv('ACCESS_SECRET')


# Validate that required tokens exist
if not BEARER_TOKEN:
    raise ValueError("BEARER_TOKEN is not set in environment variables")

def get_twitter_client():
    # Initialize the Twitter client
    return tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token=ACCESS_KEY,
        access_token_secret=ACCESS_SECRET
    )

app = Flask(__name__)

@app.route("/")
def MyTweetFeeds():
    client = get_twitter_client()
    next_token = request.args.get('next_token')
    try:
        # Get user ID
        user_info = client.get_me()
        if not user_info.data:
            raise ValueError("Could not fetch user information")
        
        user_id = user_info.data.id

        response = client.get_users_tweets(
            id=user_id,
            max_results=10,
            pagination_token = next_token,
            exclude=["retweets", "replies"],
            tweet_fields=["created_at"],
            expansions=["author_id"],
            user_fields=["profile_image_url"]
        )

        tweets = []
        if response.data:
            users = {u.id: u for u in response.includes['users']}
        
            for tweet in response.data:
                user = users[tweet.author_id]
                tweets.append({
                    'created_at':tweet.created_at.strftime('%b %d, %Y at %H:%M'),
                    'content':tweet.text,
                    'profile_image': user.profile_image_url.replace('_normal', '') if user.profile_image_url else None
                })
        return render_template('index.html', 
                                    tweets=tweets,
                                    next_token=response.meta.get('next_token') if response.meta else None)

    except Exception as e:
        return render_template('index.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
