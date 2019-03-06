from flask import redirect, url_for

from elasticsmapp.app.app import app
from elasticsmapp.app.auth import requires_auth


@app.route('/kibana', methods=['POST', 'GET'])
@requires_auth
def kibana():
    return redirect(url_for("http://localhost:5601"))


@app.route('/elastic', methods=['POST', 'GET'])
@requires_auth
def elastic():
    return redirect(url_for("http://localhost:9200"))
