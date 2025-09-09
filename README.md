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