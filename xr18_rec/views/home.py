from flask import Blueprint, render_template
from flask import current_app as app

home = Blueprint("home", __name__)

@home.route("/")
def index():
    app.logger.debug(app.config.get("ENV"))
    return render_template("index.html")
