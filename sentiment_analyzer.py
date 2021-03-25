#########################################################################
#This program analyzes sentiment in streamed tweets
#Search term, location and language parameters can be modified
#########################################################################
# The following actions are performed:
#  -Live tweets collected and stored in a csv file
#  -Text preprocessed
#  -Sentiment assigned to each tweet (Positive, Negative, Neutral)
#  -Precentages calculated
#  -Data visualized in a pie chart
#########################################################################

#import libraries
import tweepy
from tweepy.auth import OAuthHandler
from textblob import TextBlob
import pandas as pd
import re
import matplotlib.pyplot as plt
from collections import Counter

#access tokens for Twitter API (these should be stored in a separate file)
#enter your Twitter develover tokens below 
consumer_key = 'xxx'
consumer_key_secret ='xxx'
access_token = 'xxx'
access_token_secret ='xxx'

#to establish connection to Twitter API
auth = OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#set view to full text for data in dataframe
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

#create a dataframe with columns
df = pd.DataFrame(columns = ['Tweets','User_location',
                             'Tweet_date','User', 'User_ID',
                             'Tweet_ID', 'Source','User_statuses_count',
                             'User_followers', 'User_verified',
                             'Favourite_count', 'Re_tweet_count'
                            ])

#location variable for geocode with radius
London="51.5073219,-0.1276474,30mi"

#search parameter with search terms, exclude retweets
terms = ('vaccine -filter:retweets')

#function to stream tweets
def stream_tweets():
    i = 0
    for tweet in tweepy.Cursor(api.search, q=terms,
                               #enter required geolocation
                               geocode= London,
                               #exclude replies
                               exclude_replies=True,
                               #no specific time parameters- stream most recent tweets
                               since_id=None, max_id=None,
                               #display full tweet
                               tweet_mode='extended',
                               #language parameter to English
                               lang="en",
                               #100 tweets per one request to stay within Twitter API rate limits
                               count=100).items():
        print(i, end='\r')
        #create dataframe columns
        #for this project only tweet column will be used 
        df.loc[i, 'Tweets'] = tweet.full_text
        #other columns can provide further insight into users
        df.loc[i, 'User_location'] = tweet.user.location
        df.loc[i, 'Tweet_date'] = tweet.created_at
        df.loc[i, 'User'] = tweet.user.name
        df.loc[i, 'User_ID'] = tweet.user.id
        df.loc[i, 'Tweet_ID'] = tweet.id
        df.loc[i, 'Source'] = tweet.source
        df.loc[i, 'User_statuses_count'] = tweet.user.statuses_count
        df.loc[i, 'User_followers'] = tweet.user.followers_count
        df.loc[i, 'User_verified'] = tweet.user.verified
        df.loc[i, 'Favourite_count'] = tweet.favorite_count
        df.loc[i, 'Re_tweet_count'] = tweet.retweet_count
        i+=1
        #once 20k tweets is reached, break to ensure that Twitter rate limits aren't exceeded
        if i == 20000:
            break
        else:
            pass
#call the function to stream tweets        
stream_tweets()

#function to remove special chars, links and emojis, keep apostrphies in words
def clean_text(x):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z'\t])|(\w+:\/\/\S+)", " ", x).split())
#pass functiton to Tweet column to preprocess text and improve sentiment matching
df['Tweets'] = df['Tweets'].apply(lambda x: clean_text(x))

#function to analyse sentiment
def analyze_sentiment(x):
    #declare TextBlob
    analysis = TextBlob(x)
    #if the value of polarity is more than zero
    if analysis.sentiment[0]>0:
        #assign positive sentiment
        x='Positive'
    #if the value of polarity is less than zero
    elif analysis.sentiment[0]<0:
         #assign negative sentiment
        x='Negative'
    #if the value of polarity is equal to zero        
    else:
        #assign neutral sentiment
        x='Neutral'
    return (x)
#pass functiton to Tweet column in df to get values for sentiment column
df['Sentiment'] = df['Tweets'].apply(lambda x: analyze_sentiment(x))

#function to get polarity and subjectivity for each tweet
def get_polarity(x):
    analysis = TextBlob(x)
    return (analysis.sentiment)
#pass functiton to Tweet column in df to save values for Polarity/Subjectivity column
df['Polarity/Subjectivity'] = df['Tweets'].apply(lambda x: get_polarity(x))

#print first 10 records of the df for visual inspection
print (df.head(10))
#save dataframe to csv, exclude index
df.to_csv("sentiment.csv", index=False)


#function to generate word frequencies as a dictionary
def generate_freqs(text):
    #convert input text to list
    text=text.to_list()
    #split strings
    words= ' '.join(str(i) for i in text)
    #create word tokens
    word_tokens = words.split()
    #declare a counter object
    counter = Counter(word_tokens)
    #count most common
    most_frequent = counter.most_common()
    #create a dictionary
    word_dict = dict(most_frequent)
    return word_dict

word_freq=generate_freqs(df['Sentiment'])
print(word_freq)

#create a list of specific colors for the pie chart
cs = ['#ff99ff', '#b3ff99', '#ffe699']
#pass dictionary to be plotted
plt.pie([int(word_freq[v]) for v in word_freq], labels=[str(k) for k in word_freq],
        #generate precentages
        autopct='%1.1f%%',
        #set plot angle
        startangle=90,
        #set shadow for the pie chart
        shadow=True, 
        #set specific colors
        colors=cs)
# set title
plt.title('Sentiment analysis')
#layout
plt.tight_layout()
#save pie chart figure as png file
plt.savefig('sentiment.png')



