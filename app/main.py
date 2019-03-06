from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from app.app import app, db
from app.auth import *
from app.views import *


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    db.create_all()
    app.run(debug=True, port=8080)
