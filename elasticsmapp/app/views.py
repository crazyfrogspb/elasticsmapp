import requests
from flask import Response, redirect, stream_with_context, url_for

from elasticsmapp.app.app import app
from elasticsmapp.app.auth import requires_auth

kibana_server_baseurl = 'http://localhost:5601/'
elastic_server_baseurl = 'http://localhost:9200/'


@app.route('/')
@requires_auth
def index():
    return 'SMaPP Elastic Search System'


@app.route('/kibana', methods=['POST', 'GET'])
@requires_auth
def kibana():
    req = requests.get(kibana_server_baseurl, stream=True)
    return redirect(url_for(kibana_server_baseurl, _external=True))


@app.route('/elastic', methods=['POST', 'GET'])
@requires_auth
def elastic():
    req = requests.get(elastic_server_baseurl, stream=True)
    return Response(stream_with_context(req.iter_content()),
                    content_type=req.headers['content-type'])
