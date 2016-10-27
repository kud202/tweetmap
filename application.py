from flask import Flask, render_template
from jinja2 import evalcontextfilter, Markup, escape
from flask import request
from requests_aws4auth import AWS4Auth

import threading


import re

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

from elasticsearch import Elasticsearch, RequestsHttpConnection

host = 'search-kudtweet-ft7eeowl5of55zhqx2lq3fnxwm.us-east-1.es.amazonaws.com'
awsauth = AWS4Auth("AKIAJW65JL6RUPIQIVBA", "GwjVmJAmUJDSE6P3tA7DSo8whO7YHGQsckUAqxQg", "us-east-1", 'es')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

application = Flask(__name__)


@application.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

@application.route('/')
def search():
    term = request.args.get('term', "nyc")
    res = es.search(index="idx_twp2", body={"query": {"match": {'text': term }}})
    return render_template('results.html', prev_term=term, tweets=res['hits']['hits'])

if __name__ == '__main__':
    import tweet_collector as tc
    t = threading.Thread(target=tc.start)
    t.start()
    application.run()

