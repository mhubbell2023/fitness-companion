
import os
import sqlite3
import unittest
from werkzeug.security import generate_password_hash

from app import app
from models import create_tables


class TestApp(unittest.TestCase):
    """
    Unit tests for the Fitness Companion application.

    This test suite verifies core functionality:
    - User login
    - User logout
    - Viewing workout history

    A temporary SQLite database is created and seeded before each test,
    and removed after each test to ensure isolation.
    """
    def setUp(self):
        """
        Set up a fresh test environment before each test case.

        - Deletes any existing test database
        - Recreates database schema
        - Seeds a test user and workout
        - Configures Flask test client
        """
        # Remove existing test DB if it exists
        if os.path.exists("fitness.db"):
            os.remove("fitness.db")

        # Recreate tables
        create_tables()

        # Seed one test user and one workout
        conn = sqlite3.connect("fitness.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Hash password for secure storage (matches real app behavior
        hashed_password = generate_password_hash("testpass123")

        # Insert a test user
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?)
        """, ("testuser", hashed_password))

        # Retrieve generated user ID
        user_id = cursor.lastrowid

        # Insert a sample workout tied to the test user
        cursor.execute("""
            INSERT INTO workouts (user_id, exercise, sets, reps, weight, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, "Bench Press", 3, 10, 135, "2026-04-18"))

        conn.commit()
        conn.close()

        # Configure Flask app for testing
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test_secret"

        # Create test client to simulate HTTP requests
        self.client = app.test_client()

    def tearDown(self):
        """
        Clean up after each test case.

        Removes the test database to prevent data leakage
        between tests.
        """
        if os.path.exists("fitness.db"):
            os.remove("fitness.db")

    def test_user_can_login(self):
        """
        Test that a valid user can successfully log in.

        Verifies:
        - HTTP response status is 200 (success)
        - Dashboard content is present after login
        """
        response = self.client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "testpass123"
            },
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Workout", response.data)

        print("Test 1 Passed: User can log in")

    def test_user_can_logout(self):
        """
        Test that a logged-in user can log out.

        Verifies:
        - Logout route returns success status
        - User is redirected to homepage (or login page)
        """
        # Log in first
        self.client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "testpass123"
            },
            follow_redirects=True
        )

        response = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Fitness Companion", response.data)

        print("Test 2 Passed: User can log out")

    def test_user_can_see_workout_history(self):
        """
        Test that a logged-in user can view their workout history.

        Verifies:
        - Dashboard loads successfully
        - Seeded workout appears in response
        """
        # Log in first
        self.client.post(
            "/login",
            data={
                "username": "testuser",
                "password": "testpass123"
            },
            follow_redirects=True
        )

        response = self.client.get("/dashboard", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bench Press", response.data)

        print("Test 3 Passed: Workout history is visible")


if __name__ == "__main__":
    unittest.main() 