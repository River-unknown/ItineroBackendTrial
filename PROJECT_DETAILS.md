# Itinero Backend: Architecture, Design, and Development Deep-Dive

This document provides a detailed overview of the Itinero backend, covering the architectural decisions, design rationale, API specification, and challenges overcome during development.

---

## 1. Architecture & Design Choices

The application was designed as a modern, stateless, and scalable backend API following professional software engineering principles.

### Backend Technology
* **Flask:** Chosen for its lightweight, "unopinionated" nature, making it ideal for building REST APIs.
* **Flask-SQLAlchemy:** Used as the Object-Relational Mapper (ORM) to interact with the database using Python classes (Models) instead of raw SQL.
* **Modularity (App Factory & Blueprints):** The project was structured using an App Factory pattern (`create_app`) and Blueprints to separate concerns, making the codebase cleaner and easier to scale.

### Database
* **PostgreSQL:** Chosen for its robustness, reliability, and advanced features, making it a professional standard for production applications.
* **Docker & Docker Compose:** Containerizing the PostgreSQL database was a critical architectural choice to ensure an isolated, consistent, and reproducible development environment for any user.
* **Flask-Migrate & Alembic:** Integrated for database schema management, allowing for version-controlled, non-destructive updates to the database structure.

### Security Design
* **Password Hashing (Bcrypt):** User passwords are never stored in plain text. They are securely hashed using `Bcrypt`, an adaptive algorithm resistant to brute-force attacks.
* **Authentication (JWT):** The API is secured using JSON Web Tokens, enabling a **stateless** authentication model perfect for decoupled architectures and scalability.
* **Data Ownership & Authorization:** Every protected endpoint includes a crucial security check (e.g., `if itinerary.owner_id != current_user.id:`) to ensure users can only access their own data.

---

## 2. API Specification & Workflow

The API is designed to be RESTful and serves as the brain for the Itinero application.

### API Endpoints

#### Authentication
* **`POST /api/register`**
    * **Description:** Creates a new user account.
    * **Auth:** `Public`
    * **Request Body:** `{ "username": "...", "email": "...", "password": "..." }`
    * **Success Response:** `201 Created`

* **`POST /api/login`**
    * **Description:** Authenticates a user and returns a JWT.
    * **Auth:** `Public`
    * **Request Body:** `{ "email": "...", "password": "..." }`
    * **Success Response:** `200 OK` - `{ "token": "ey..." }`

#### Itineraries
* **`POST /api/itineraries`**
    * **Description:** Creates a new, AI-generated itinerary for the authenticated user.
    * **Auth:** `Protected (Bearer Token)`
    * **Request Body:** `{ "trip_name": "...", "city": "...", "duration_days": 3, "interests": "..." }`
    * **Success Response:** `201 Created` - Returns the full, newly created itinerary object.

* **`GET /api/itineraries`**
    * **Description:** Gets a list of all itineraries for the authenticated user.
    * **Auth:** `Protected (Bearer Token)`
    * **Success Response:** `200 OK` - `{ "itineraries": [...] }`

* **`GET /api/itineraries/<int:trip_id>`**
    * **Description:** Gets a single, specific itinerary by its ID.
    * **Auth:** `Protected (Bearer Token)`
    * **Success Response:** `200 OK` - Returns the single itinerary object.

* **`PUT /api/itineraries/<int:trip_id>`**
    * **Description:** Updates the name of an existing itinerary.
    * **Auth:** `Protected (Bearer Token)`
    * **Request Body:** `{ "trip_name": "New Name" }`
    * **Success Response:** `200 OK`

* **`DELETE /api/itineraries/<int:trip_id>`**
    * **Description:** Deletes an itinerary and all its associated destinations.
    * **Auth:** `Protected (Bearer Token)`
    * **Success Response:** `200 OK`

### Typical Frontend Workflow
A frontend application (e.g., a React app) would interact with this API by first registering/logging in a user to get a JWT. That token would be stored in the browser's `localStorage` and automatically attached as a `Bearer Token` to all subsequent protected requests. A logout would simply delete the token from storage.

---

## 3. Development Process & Challenges Faced

The development process was iterative, highlighting the importance of methodical debugging.

### Challenge 1: The Great Connection Saga
* **Initial Problem:** The application consistently failed with a `FATAL: password authentication failed for user "itinero_admin"` error.
* **Initial Hypothesis:** The problem was a state mismatch between the `.env` file and the Docker container's persistent data volume. It was assumed the container was using an old, incorrect password.
* **Debugging Steps:**
    1.  Multiple attempts were made to reset the database by destroying the container and its volume (`docker-compose down -v`, `docker volume prune`).
    2.  The `.env` file was simplified (removing quotes and special characters) to rule out parsing errors.
    3.  The credentials were hard-coded into `docker-compose.yml` to force the container to initialize with the correct password.
* **The Twist:** Despite all these measures, the password error persisted. This invalidated the initial hypothesis and proved the problem was not a password mismatch. If the database was being created fresh with a known password, and the app was using that same password, a failure meant the app **was not talking to the correct database**.
* **Root Cause:** A "zombie" PostgreSQL server from a previous local installation was still running as a Windows service and had captured port `5432`. The Python app was connecting to this old server, which had no knowledge of the correct user or password, instead of the Docker container.
* **Solution:** The local `postgresql` service was located in the Windows Services manager (`services.msc`), **Stopped**, and **Disabled**. This freed port `5432`, allowing the Docker container to bind to it correctly. The Python app then connected to the right database, and the authentication succeeded immediately.

### Challenge 2: Minor Logic Bugs
* **Inverted Login Logic:** The initial `/login` route was coded with inverted logic (`if user or...`), which issued tokens for *incorrect* passwords. This was fixed by changing the conditional to `if user and user.check_password...`.
* **Model vs. Route Mismatch:** A `500 Internal Server Error` was traced back to a route trying to use a `title` field when the database model and other routes expected `trip_name`. This was corrected to ensure consistency across the application.

---

## 4. Final API Design
* **Stateless by Design:** Every request contains all the information needed to process it. The server maintains no session state, which is crucial for reliability and scalability.
* **Robust Error Handling:** The AI-powered itinerary creation route is wrapped in a `try...except` block with a `db.session.rollback()` to prevent crashes and maintain data integrity if the external API fails.
* **Developer-Friendly JSON:** API response keys were explicitly renamed (e.g., from `id` to `itinerary_id`) to avoid ambiguity and improve clarity for frontend developers.