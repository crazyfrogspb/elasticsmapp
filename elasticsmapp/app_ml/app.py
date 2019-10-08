from os import environ as env

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from flask import Flask, render_template, request

load_dotenv(find_dotenv())


if True:
    from elasticsmapp.utils.queries import find_similar_documents

app = Flask(__name__)

PORT = int(env.get("PORT", 8080))
DEBUG_MODE = int(env.get("DEBUG_MODE", 1))


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['embedding']
        daterange = request.form['daterange'].split('-')
        exclude = request.form.get('exclude_check')
        date_start = daterange[0].strip()
        date_end = daterange[-1].strip()
        platforms = request.form.getlist('platforms')
        if text is None:
            return render_template('index.html', error='You need to type text')

        results = find_similar_documents(
            text, date_start, date_end, platforms, exclude)
        if results is None:
            return render_template('index.html', error='No indices found for this selection')
        else:
            results_flat = []
            results = results.get('hits', {}).get('hits')
            if results is None:
                return render_template('index.html', error='No results')
            for post in results:
                res = {'_id': post['_id']}
                for field, value in post['_source'].items():
                    res[field] = value
                results_flat.append(res)
            with pd.option_context('display.max_colwidth', 100):
                return render_template("results.html", text=text, data=pd.DataFrame(results_flat).to_html(), error='')
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG_MODE)
