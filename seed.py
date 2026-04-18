from database import get_db_connection
from models import create_tables
from database import get_db_connection
from werkzeug.security import generate_password_hash


def seed_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create or reuse a test user
    username = "testuser"
    password = generate_password_hash("password123")

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        user_id = user["id"]
    else:
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, (username, password))
        user_id = cursor.lastrowid

    # Optional: clear old workouts for that user first
    cursor.execute("DELETE FROM workouts WHERE user_id = ?", (user_id,))

    fake_workouts = [
        (user_id, "Bench Press", 3, 8, 135, "2026-04-01"),
        (user_id, "Bench Press", 3, 8, 145, "2026-04-05"),
        (user_id, "Bench Press", 3, 6, 155, "2026-04-10"),
        (user_id, "Squat", 3, 8, 185, "2026-04-02"),
        (user_id, "Squat", 3, 8, 205, "2026-04-07"),
        (user_id, "Squat", 3, 5, 225, "2026-04-12"),
        (user_id, "Deadlift", 3, 5, 225, "2026-04-03"),
        (user_id, "Deadlift", 3, 5, 245, "2026-04-09"),
        (user_id, "Deadlift", 3, 5, 275, "2026-04-14"),
        (user_id, "Shoulder Press", 3, 10, 75, "2026-04-04"),
        (user_id, "Shoulder Press", 3, 8, 85, "2026-04-11"),
        (user_id, "Pull Ups", 3, 10, 0, "2026-04-06"),
        (user_id, "Pull Ups", 3, 12, 0, "2026-04-13"),
    ]

    cursor.executemany("""
        INSERT INTO workouts (user_id, exercise, sets, reps, weight, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, fake_workouts)

    conn.commit()
    conn.close()

    print("Seeded test user and fake workouts successfully.")


if __name__ == "__main__":
    seed_data()