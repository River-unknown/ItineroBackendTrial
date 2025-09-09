# Itinero - AI Travel Planner Backend

This is the Flask backend for an AI-powered travel itinerary planner. It provides a secure API for user authentication and dynamically generates travel plans using the Google Gemini API, saving all data to a PostgreSQL database.

---

## Technology Stack
* **Backend:** Python 3, Flask, Flask-SQLAlchemy
* **Database:** PostgreSQL (running in Docker)
* **API Auth:** JSON Web Tokens (JWT)
* **AI:** Google Gemini API
* **Other:** Docker Compose, Flask-CORS

---

## How to Run This Project

1.  **Clone the repo:**
    `git clone <your-repo-url>`
2.  **Create your environment file:**
    `cp .env.example .env`
3.  **Edit the `.env` file:** Add your `SECRET_KEY`, `API_KEY`, and a strong `POSTGRES_PASSWORD`.
4.  **Start the database:**
    `docker-compose up -d`
5.  **Set up the Python environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # (or .\venv\Scripts\activate on Windows)
    pip install -r requirements.txt
    ```
6.  **Apply Database Migrations:** This command will create all the tables based on your version history.
    `flask db upgrade`
7.  **Run the application:**
    `python run.py`

The API will be running at `http://127.0.0.1:5000`.

---

## Development & Problem Log

This is where to track progress and problems faced, just as you wanted.

### 2025-09-09: AI Integration
* **Update:** Successfully built the core `POST /api/itineraries` endpoint. The route is now secured, takes user input (city, interests), calls the Gemini API, parses the JSON response, and populates the `destinations` table in the database.
* **Problem:** Ran into a `500 Error` after login.
* **Solution:** The `POST` route was using `Itinerary(title=...)` while the `GET` route and Model expected `trip_name=...`. This mismatch caused a `TypeError` when creating the object. Fixed the route to use the correct column names.

### 2025-09-09: Database Hell Debugging
* **Problem:** Constant `FATAL: password authentication failed` errors, even after resetting Docker volumes.
* **Solution:** The issue was a "zombie" local PostgreSQL server (from a manual install) that had captured port `5432`. The Python app was talking to this dead server, not the Docker container. The fix was to go into `services.msc` on Windows, **Stop**, and **Disable** the local `postgresql` service, freeing the port for Docker.