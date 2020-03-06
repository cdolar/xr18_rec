from flask import Flask

def create_app(testing=False):
    app = Flask(__name__)

    from xr18_rec.views.home import home
    app.register_blueprint(home)

    from xr18_rec.views.api import api
    app.register_blueprint(api, url_prefix="/api")

    return app


if __name__ == "__main__":
    app.run()