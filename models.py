
from database import get_db_connection

def create_tables():
    """
    Create required database tables if they do not already exist.

    This function initializes the SQLite database schema by creating:
    - A `users` table for authentication data
    - A `workouts` table for storing user workout logs

    The function is safe to call multiple times due to the use of
    `CREATE TABLE IF NOT EXISTS`.

    Returns:
        None
    """
    # Establish database connection
    conn = get_db_connection()
    cursor = conn.cursor()

    # USERS TABLE:
    # Stores login credentials for each user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique user ID
            username TEXT UNIQUE NOT NULL, -- Username for login (must be unique)
            password TEXT NOT NULL -- Hashed password for security
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique workout ID
            user_id INTEGER NOT NULL, -- Foreign key linking to users table
            exercise TEXT NOT NULL, -- Name of the exercise performed
            sets INTEGER NOT NULL, -- Number of sets performed
            reps INTEGER NOT NULL, -- Number of repetitions per set
            weight REAL NOT NULL, -- Weight used for the exercise
            date TEXT NOT NULL, -- Date when the workout was performed
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Save changes and close connection
    conn.commit()
    conn.close()

