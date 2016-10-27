#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textwrap import TextWrapper

from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

host = 'ELASTIC-SEARCH-HOST-ON-AWS'
awsauth = AWS4Auth("IAM_ACCESS_KEY", "IAM_SECRET", "us-east-1", 'es')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
print(es.info())

#Variables that contains the user credentials to access Twitter API
access_token = "TWITTER-ACCESS-TOKEN"
access_token_secret = "TWITTER-TOKEN-SECRET"
consumer_key = "TWITTER_CONSUMER-KET"
consumer_secret = "TWITTER-SECRET"

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
    status_wrapper = TextWrapper(width=60, initial_indent='    ', subsequent_indent='    ')

    def on_status(self, status):
        try:
            json_data = status._json
            if json_data['geo'] is not None:
                es.create(index="idx_twp2",
                          doc_type="twitter_twp",
                          id=json_data['id'],
                          body=json_data)
        except Exception as e:
            print(e)


def start():
    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['nyc', 'brooklyn', 'nyu'])
