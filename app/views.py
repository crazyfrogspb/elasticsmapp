from flask import redirect

from elasticsmapp.app.app import app
from elasticsmapp.app.auth import requires_auth


@app.route('/kibana', methods=['POST', 'GET'])
@requires_auth
def kibana():
    return redirect("http://localhost:5601")


@app.route('/elastic', methods=['POST', 'GET'])
@requires_auth
def elastic():
    return redirect("http://localhost:9200")
