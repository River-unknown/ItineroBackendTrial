import os
from dotenv import load_dotenv  # Import dotenv here

# --- NEW LOADING LOGIC ---
# Find the .env file in this same (root) directory and load it.
# This MUST happen BEFORE we import the app.
basedir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(basedir, '.env')
load_dotenv(env_path)
# --- END NEW LOGIC ---


# Now we import the app. By this point, all environment variables are loaded.
from app import create_app, db
from app.models import User, Itinerary, Destination # Import models
print("POSTGRES_USER:", os.getenv("POSTGRES_USER"))
print("POSTGRES_PASSWORD:", os.getenv("POSTGRES_PASSWORD"))
print("POSTGRES_DB:", os.getenv("POSTGRES_DB"))

app = create_app()


if __name__ == '__main__':
    app.run(debug=True, port=5000)