import datetime

import pandas as pd
from flask import Flask, render_template, request

import config
from elasticsmapp.utils.queries import find_similar_documents

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['embedding']
        date = request.form['day']
        platform = request.form['platform_select']
        if text is None or date == '':
            return render_template('index.html', error='You need to type text and choose date')

        date = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
        status_code, results = find_similar_documents(text, date, platform)
        results_flat = []
        for post in results['hits']['hits']:
            res = {'_id': post['_id']}
            for field, value in post['_source'].items():
                res[field] = value
            results_flat.append(res)
        if status_code == 400:
            return render_template('index.html', error='Index for this data and platform does not exist')
        else:
            return render_template("results.html", text=text, data=pd.DataFrame(results_flat), error='')
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)