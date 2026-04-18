"""
Fitness Companion Web Application

This Flask application allows users to:
- Register and log in securely
- Add, edit, and delete workouts
- View workout history on a dashboard

Dependencies:
- Flask
- SQLite (via database.py)
- werkzeug.security for password hashing
"""

from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import create_tables
from database import get_db_connection

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Create database tables when app starts
create_tables()


@app.route('/')
def home():
    """
    Render the home page.

    Returns:
        HTML: Home page template.
    """
    return render_template('home.html')


@app.route('/add_workout', methods=['GET', 'POST'])
def add_workout():
    """
    Handle adding a new workout.

    - GET: Displays the workout form
    - POST: Inserts workout into database

    Returns:
        Redirect to dashboard or rendered template.
    """
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extract form data
        exercise = request.form['exercise']
        sets = request.form['sets']
        reps = request.form['reps']
        weight = request.form['weight']
        date = request.form['date']

        # Insert workout into database
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO workouts (user_id, exercise, sets, reps, weight, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session['user_id'], exercise, sets, reps, weight, date))

        conn.commit()
        conn.close()

        return redirect(url_for('dashboard'))

    return render_template('add_workout.html')


@app.route('/dashboard')
def dashboard():
    """
    Display the user's workout dashboard.

    Retrieves all workouts for the logged-in user,
    ordered by most recent.

    Returns:
        HTML: Dashboard page with workout data.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM workouts
        WHERE user_id = ?
        ORDER BY date DESC, id DESC
    """, (session['user_id'],))

    workouts = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', workouts=workouts)


@app.route('/delete_workout/<int:workout_id>')
def delete_workout(workout_id):
    """
    Delete a specific workout.

    Args:
        workout_id (int): ID of the workout to delete.

    Returns:
        Redirect to dashboard.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM workouts
        WHERE id = ? AND user_id = ?
    """, (workout_id, session['user_id']))

    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))


@app.route('/edit_workout/<int:workout_id>', methods=['GET', 'POST'])
def edit_workout(workout_id):
    """
    Edit an existing workout.

    - GET: Display existing workout data
    - POST: Update workout in database

    Args:
        workout_id (int): ID of the workout to edit.

    Returns:
        HTML or redirect response.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch workout for current user
    cursor.execute("""
        SELECT * FROM workouts
        WHERE id = ? AND user_id = ?
    """, (workout_id, session['user_id']))
    workout = cursor.fetchone()

    # Prevent unauthorized access
    if not workout:
        conn.close()
        return "Workout not found or unauthorized."

    if request.method == 'POST':
        # Updated form data
        exercise = request.form['exercise']
        sets = request.form['sets']
        reps = request.form['reps']
        weight = request.form['weight']
        date = request.form['date']

        # Update database record
        cursor.execute("""
            UPDATE workouts
            SET exercise = ?, sets = ?, reps = ?, weight = ?, date = ?
            WHERE id = ? AND user_id = ?
        """, (exercise, sets, reps, weight, date, workout_id, session['user_id']))

        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit_workout.html', workout=workout)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.

    - GET: Show login form
    - POST: Authenticate user

    Returns:
        Redirect to dashboard or error message.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve user by username
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        # Validate password hash
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))

        return "Invalid username or password."

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle user registration.

    - GET: Show registration form
    - POST: Create new user account

    Returns:
        Redirect to dashboard or error message.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (?, ?)
            """, (username, hashed_password))
            conn.commit()

            # Automatically log user in after registration
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            session['username'] = username

            conn.close()
            return redirect(url_for('dashboard'))

        except:
            conn.close()
            return "Username already exists."

    return render_template('register.html')


@app.route('/logout')
def logout():
    """
    Log the user out by clearing the session.

    Returns:
        Redirect to home page.
    """
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    # Run app in debug mode for development
    app.run(debug=True)
