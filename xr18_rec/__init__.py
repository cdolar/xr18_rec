from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MySecretKey!'

socketio = SocketIO(app)

from xr18_rec.views.home import home
app.register_blueprint(home)

from xr18_rec.views.api import api
app.register_blueprint(api, url_prefix="/api")

# def create_app(testing=False):
#     app = Flask(__name__)

#     from xr18_rec.views.home import home
#     app.register_blueprint(home)

#     from xr18_rec.views.api import api
#     app.register_blueprint(api, url_prefix="/api")

#     return app
