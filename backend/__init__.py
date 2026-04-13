from flask import Flask
from flask_cors import CORS
from backend.models import db
from backend.routes.api import api_bp
import os

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configure SQLite database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'meetup.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    app.register_blueprint(api_bp)
    
    return app
