from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import Config 
from flask_migrate import Migrate 

# Create extension instances WITHOUT attaching them to an app yet.
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
def create_app(config_class=Config):
    """
    This is the application factory. It creates and configures the Flask app.
    """
    app = Flask(__name__)
    
    # 1. Load configuration from our config.py file
    app.config.from_object(config_class)

    # 2. Initialize our extensions (db, bcrypt) with THIS app instance
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)  # Initialize Flask-Migrate
    # 3. Import and register our Blueprint(s)
    from .routes import main_bp  # Import the blueprint
    app.register_blueprint(main_bp, url_prefix='/api') # Register it
    # Note: url_prefix='/api' means ALL routes in that file will now start with /api
    # So /login becomes /api/login, /itineraries becomes /api/itineraries, etc.
    # This is great practice for versioning your API!

    # 4. Return the configured app instance
    return app