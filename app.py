from flask import Flask
from flask_migrate import Migrate

from config import Config
from models import db
from csv_to_db import data_cli


app = Flask(__name__)
app.config.from_object(Config)
app.cli.add_command(data_cli)
db.init_app(app)
migrate = Migrate(app, db)


from views import *


if __name__ == '__main__':
    app.run(debug=True, port=8080)
