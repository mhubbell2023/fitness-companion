
import sqlite3


def get_db_connection():
    """Create and return a connection to the SQLite database."""
    # Connect to the SQLite database file
    conn = sqlite3.connect("fitness.db")

    # Enable dictionary-style row access (e.g., row['column_name'])
    conn.row_factory = sqlite3.Row
    return conn