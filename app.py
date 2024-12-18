from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mood_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# MoodEntry Model
class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    mood = db.Column(db.String(100), nullable=False)
    hours_slept = db.Column(db.Float, nullable=False, default=0.0)
    notes = db.Column(db.Text, nullable=True)

# Initialize the database
with app.app_context():
    db.create_all()

# Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists. Please choose another one.', 'error')
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html')

# Protected Mood Tracker
@app.route('/')
@login_required
def index():
    entries = MoodEntry.query.all()
    total_entries = len(entries)

    mood_values = {
        "Happy": 5,
        "Excited": 4,
        "Calm": 3,
        "Anxious": 2,
        "Sad": 1,
        "Angry": 0
    }

    if total_entries > 0:
        total_mood_value = sum(mood_values.get(entry.mood, 0) for entry in entries)
        average_mood = round(total_mood_value / total_entries, 2)
    else:
        average_mood = 0

    average_hours_slept = round(sum(entry.hours_slept for entry in entries) / total_entries, 2) if total_entries > 0 else 0

    return render_template('index.html', total_entries=total_entries, average_mood=average_mood, average_hours_slept=average_hours_slept)

# Mood Tracker Page
@app.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    if request.method == 'POST':
        date = request.form['date']
        mood = request.form['mood']
        hours_slept = request.form.get('hours_slept', type=float)
        notes = request.form['notes']

        if not mood:
            flash('Mood is required!', 'error')
            return redirect(url_for('tracker'))

        try:
            parsed_date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'error')
            return redirect(url_for('tracker'))

        new_entry = MoodEntry(date=parsed_date, mood=mood, hours_slept=hours_slept, notes=notes)
        db.session.add(new_entry)
        db.session.commit()
        flash('Mood entry added successfully!', 'success')
        return redirect(url_for('tracker'))

    entries = MoodEntry.query.all()
    return render_template('tracker.html', entries=entries)

# Edit Mood Entry
@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    entry = MoodEntry.query.get_or_404(entry_id)
    if request.method == 'POST':
        try:
            entry.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', 'error')
            return redirect(url_for('edit_entry', entry_id=entry_id))

        entry.mood = request.form['mood']
        entry.hours_slept = request.form.get('hours_slept', type=float)
        entry.notes = request.form['notes']
        db.session.commit()
        flash('Mood entry updated successfully!', 'success')
        return redirect(url_for('tracker'))
    return render_template('edit_entry.html', entry=entry)

# Delete Mood Entry
@app.route('/delete_entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_entry(entry_id):
    entry = MoodEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash('Mood entry deleted successfully!', 'success')
    return redirect(url_for('tracker'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)
