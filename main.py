import os
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopementConfig
from application.database import db
#from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from flask_login import LoginManager
from application.models import User
#from flask_wtf.csrf import CSRFProtect

app = None
api = None
login_manager = LoginManager()

def Create_app():
    app = Flask(__name__, template_folder = "templates")
    if os.getenv('ENV') == "production":
        raise Exception("Currently no production config is setup")
    else:
        print("Starting Local Developement")
        app.config.from_object(LocalDevelopementConfig)
    
    db.init_app(app)
    api = Api(app)
    app.app_context().push()
    #user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
    #security = Security(app, user_datastore)
    #csrf = CSRFProtect(app)
    
    login_manager.init_app(app)
    return app, api

app, api = Create_app()

# Import all the controllers so they are loaded
from application.controllers import *

"""
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def not_allowed(e):
    return render_template('403.html'), 403

"""


@app.errorhandler(401)
def unauthorized(e):
    return render_template('login.html')


from application.api import UserAPI
api.add_resource(UserAPI, "/api/user", "/api/user/<string:username>")

from application.api import DeckAPI
api.add_resource(DeckAPI, "/api/deck", "/api/deck/<int:id>")

from application.api import CardAPI
api.add_resource(CardAPI, "/api/card", "/api/card/<int:id>")

from application.api import DeckScoreAPI
api.add_resource(DeckScoreAPI, "/api/deck/score/<int:id>")

if __name__ == '__main__':
    #Run the Flask app
    app.run(
        host = '0.0.0.0',
        debug = True
    )

