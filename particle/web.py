import flask
import redis
import json
from flask import request
import dateutil.parser
from particle.helpers import *
from particle.common import db, CONFIG, APP_DEBUG

app = flask.Flask(__name__)

class JSONEncoder(json.JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def encode(self, obj):
        if hasattr(obj, 'to_dict'):
            obj = obj.to_dict()
        return super(JSONEncoder, self).encode(obj)

    def default(self, obj):
        if hasattr(obj, 'as_dict'):
            return obj.as_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        raise TypeError("%r is not JSON serializable" % obj)


def jsonify(obj, status=200, headers=None):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    jsondata = json.dumps(obj, cls=JSONEncoder)
    if 'callback' in request.args:
        jsondata = '%s(%s)' % (request.args.get('callback'), jsondata)
    return Response(jsondata, headers=headers,
                    status=status, mimetype='application/json')

@app.route("/")
def query():

  # parse args
  article_slug = sluggify(request.args.get('url', ''))
  data_sources = request.args.get('data_sources', 'all').split(",")
  start = request.args.get('start', 0)
  end = request.args.get('end', 1e11)
  order = request.args.get('order', 'desc')
  include_article = request.args.get('order', 'true').lower()
  include_keys = request.args.get('include_keys', 'true').lower()
  
  # pesky boolian problem
  if include_keys=='true':
    include_keys = True
  elif include_keys=='false':
    include_keys = False

  # parse article arg
  if include_article == 'true':
    include_article = True
  elif include_article =='false':
    include_article = False
  else:
    include_article = False

  # fetch data
  results = db.zrangebyscore(article_slug, min = start, max = end)

  # optionally filter out particular datasources
  if data_sources[0] != "all":
    print data_sources
    filtered_results = []
    data = [json.loads(r) for r in results]
    print data
    for src in data_sources:
      for d in data:
        if d.has_key(src):
          if not include_keys:
            filtered_results.append(json.dumps(d[src]))
          else:
            filtered_results.append(json.dumps(d))

      results = filtered_results

  # optionally order database
  if order=='desc':
    results = [r for r in reversed(results)]
  
  # turn it into a json list
  results = "[%s]" % ",".join(results)

  # create article dict if requested
  if include_article:
    return_pattern = "{\"article\" : %s, \"events\" : %s }"
    article_data = db.get(article_slug+":article")
    
    if article_data is None:
      article_data = "{}"
    
    return return_pattern % (article_data, results)

  # otherwise just return json list
  else: 
    return results

@app.route("/recent_articles/")
def recent():
  # parse args
  start = request.args.get('start', 0)
  end = request.args.get('end', 1e11)
  order = request.args.get('order', 'desc')
  
  # fetch data
  key ='article_sorted_set'
  results = db.zrangebyscore(key, min = start, max = end)

  if order=='desc':
    results = [r for r in reversed(results)]

  # turn it into a json list
  return "[%s]" % ",".join(results[0:21])

if __name__ == "__main__":
  if APP_DEBUG:
    app.debug = True
  app.run(host='0.0.0.0', port=5000)