from JumpScale import j
import os

from eve import Eve
from eve.render import send_response

from flask.ext.bootstrap import Bootstrap
# from eve_docs import eve_docs
from eve_docs.config import get_cfg
from generators.EveGenerator import generateDomain
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
from flask import render_template

from JumpScale.baselib import cmdutils

# default eve settings
import JumpScale.grid.osis
import sys

def run(port=5000, mongo_host='localhost', mongo_port=27017, pagination_limit=1000000):
    client = j.clients.osis.getByInstance('main')

    apps = dict()
    
    for namespace in client.listNamespaces():
        spec=client.getOsisSpecModel(namespace)
        dbname = namespace if namespace != 'system' else 'js_system'
        my_settings = {
                'MONGO_HOST': mongo_host,
                'MONGO_PORT': mongo_port ,
                'MONGO_DBNAME': dbname,
                'DOMAIN': generateDomain(spec),
                'RESOURCE_METHODS': ['GET', 'POST'],
                'ITEM_METHODS': ['GET', 'PATCH', 'PUT', 'DELETE'],
                'X_DOMAINS': '*',
                'MONGO_QUERY_BLACKLIST': [],
                'X_HEADERS': ["X-HTTP-Method-Override", 'If-Match'],
                'PAGINATION_LIMIT': pagination_limit
        }
    
        # init application
        app = Eve(__name__, settings=my_settings)
    
        Bootstrap(app)
    
        @app.route('/ui')
        def ui():
            return render_template('ui.html')
    
        # Unfortunately, eve_docs doesn't support CORS (too bad!), so we had to reimplement it ourselves
        @app.route('/docs/spec.json')
        def specs():
            return send_response(None, [get_cfg()])
    
        apps['/%s' % namespace] = app 
    
    print("visit:\nhttp://localhost:%s/docs/" % port)
    if apps:
        firstapp = list(apps.values())[0]
        application = DispatcherMiddleware(firstapp, apps)
    # let's roll
        run_simple('0.0.0.0', port, application, use_reloader=False)

if __name__ == "__main__":
    parser = cmdutils.ArgumentParser()
    parser.add_argument("-p", '--port', help='Port', default=5000, type=int)
    parser.add_argument("-dh", '--mongo_host', help='Mongodb hostname', default='localhost')
    parser.add_argument("-dp", '--mongo_port', help='Mongodb port', default=27017, type=int)
    parser.add_argument("-pl", '--pagination_limit', help='pagination limit', default=1000000, type=int)
    parser.add_argument("--mongodb_config")
    opts = parser.parse_args()
    port = opts.port
    if opts.mongodb_config:
        mongodb_config = j.application.getAppInstanceHRD('mongodb_client', opts.mongodb_config)
        mongo_host = mongodb_config.get('instance.param.addr')
        mongo_port = mongodb_config.get('instance.param.port')
    else:
        mongo_host = opts.mongo_host
        mongo_port = opts.mongo_port
    pagination_limit = opts.pagination_limit

    run(port=port, mongo_host=mongo_host, mongo_port=mongo_port, pagination_limit=pagination_limit)
