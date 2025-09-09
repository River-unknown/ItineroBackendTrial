# Developer Operations Guide & Future Notes

This document is a technical guide for the future developer (or my future self) maintaining the Itinero backend. It covers environment specifics, common workflows, and future plans.

---

## 1. Environment Recreation & Versioning

The `README.md` provides the basic setup, but in 6+ months, dependency versions will have changed. To guarantee this project runs, here are the specifics:

### Version Pinning
* **PostgreSQL:** The `docker-compose.yml` file currently uses `postgres:latest`. To ensure a consistent database version, this should be pinned. At the time of writing (Sept 2025), a good choice would be `postgres:16`. Update your `docker-compose.yml` to reflect this.
* **Python:** This project was developed with a specific Python version. Create a file named `.python-version` in the root directory and add the version number (e.g., `3.11.4`) to ensure tools like `pyenv` can automatically pick it up.

### Key Dependencies
* **Docker Desktop:** This is required to run the `docker-compose` environment. Ensure it's installed and running before starting the project.

---

## 2. API Testing with Postman

To avoid re-creating all API tests from scratch, the Postman collection should be saved within the repository.

### Workflow
1.  **Export the Collection:** In Postman, find your "Itinero" collection, click the three dots (`...`), and select "Export." Save the file as `Itinero_API.postman_collection.json` in the project's root directory.
2.  **Export the Environment:** On the "Environments" tab, select your "Itinero Dev" environment and export it as `Itinero_Dev.postman_environment.json`.
3.  **Commit these files** to the repository. Your future self can now just import these two files to get the entire testing suite back instantly.

**Remember the Automated Auth Flow:**
1.  Ensure the "Itinero Dev" environment is active in Postman.
2.  Run the `POST /api/login` request once.
3.  The `jwt_token` variable will be automatically saved.
4.  All other protected requests will use this token automatically via the `{{jwt_token}}` variable.

---

## 3. Database Management Workflow

All database changes are managed by Flask-Migrate. **Do not manually edit the database schema.**

### The Migration Process
When you change a model in `app/models.py` (e.g., add a new column):
1.  **Generate the migration script:**
    `flask db migrate -m "A short message describing the change"`
2.  **Review the script:** Check the newly generated file in `migrations/versions/` to ensure it looks correct.
3.  **Apply the migration to the database:**
    `flask db upgrade`

### How to Reset the Database (The "Nuke" Option)
If you are in early development and need a completely fresh start (this will delete ALL data):
1.  `docker-compose down -v` (The `-v` is critical; it deletes the data volume).
2.  `docker-compose up -d`
3.  `flask db upgrade` (This applies all migrations from scratch).

### How to Connect Directly to the Database
To debug or view data directly in the `psql` shell:
1.  Make sure the container is running.
2.  Run this command:
    `docker exec -it itinero-db-service psql -U itinero_admin -d itinero_db`
3.  It will ask for the password, which is in your `.env` file. You are now inside the database. Use commands like `\dt` to see tables or `SELECT * FROM users;` to see data.

---

## 4. Managing Secrets & Keys

* **`.env.example`:** This file is the template. When setting up on a new machine, copy this file to `.env` and fill in the secret values.
* **`SECRET_KEY`:** This can be any long, random string. You can generate a new one with `python -c 'import secrets; print(secrets.token_hex(32))'`.
* **`API_KEY`:** This is your **Google Gemini API Key**. You can get this from the Google AI Studio dashboard. Ensure the API key has permissions for the "Generative Language API."

---

## 5. Future Roadmap & TODOs

This is a reminder of the planned next steps.

* **[ ] Build Full CRUD for Destinations:**
    * `POST /api/itineraries/<id>/destinations` (Add a destination)
    * `PUT /api/destinations/<id>` (Edit a destination's notes/day)
    * `DELETE /api/destinations/<id>` (Delete a single destination)

* **[ ] Build the Frontend Application:**
    * Use `npx create-react-app` in a separate folder.
    * Build components for Login, Register, Dashboard, and CreateItineraryForm.
    * Use `axios` for API calls.
    * Implement the JWT storage/retrieval logic in `localStorage`.

* **[ ] V2.0 - Advanced Features:**
    * **Asynchronous AI Calls:** Refactor the Gemini API call into a background task using **Celery & Redis** to prevent long waits on the frontend.
    * **Real-Time Collaboration:** Integrate **Flask-SocketIO** to allow multiple users to edit the same itinerary and see changes live.
    * **Input Validation:** Add a schema validation library like **Marshmallow** or **Pydantic** to the API routes for more robust error checking of incoming data.