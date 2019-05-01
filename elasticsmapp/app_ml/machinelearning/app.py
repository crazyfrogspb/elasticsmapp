import numpy as np
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
        if text is None or date is None:
            return render_template('index.html', error=['You need to type text and choose date'])

        x = pd.DataFrame(np.random.randn(20, 5))
        return render_template("results.html", text=text, data=x.to_html(), error=None)
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
