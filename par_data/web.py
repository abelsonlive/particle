import flask
import redis
import json
from flask import request
import dateutil.parser
from par_data.helpers import *
from par_data.common import db, CONFIG, APP_DEBUG

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

# data_sources = [
#   'internal_facebook',
#   'internal_facebook_insights',
#   'internal_twitter',
#   'internal_pages',
#   'external_pages'
# ]

@app.route("/")
def query():
  # parse args
  article_slug = sluggify(request.args.get('url', ''))
  data_sources = request.args.get('data_sources', 'all').split(",")
  start = request.args.get('start', 0)
  end = request.args.get('end', 1e11)
  order = request.args.get('order', 'desc')
  include_keys = request.args.get('include_keys', True)
  if include_keys.lower()== 'false': include_keys = False

  
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

  if order=='desc':
    results = [r for r in reversed(results)]

  # turn it into a json list
  return "[%s]" % ",".join(results)

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