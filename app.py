from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mood_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)  # Store date as a string (YYYY-MM-DD)
    mood = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    entries = MoodEntry.query.all()
    total_entries = len(entries)
    
    # Calculate average mood (assuming mood is a string, we can assign numerical values)
    mood_values = {
        "Happy": 5,
        "Excited": 4,
        "Calm": 3,
        "Anxious": 2,
        "Sad": 1,
        "Angry": 0
    }
    
    if total_entries > 0:
        total_mood_value = sum(mood_values[entry.mood] for entry in entries)
        average_mood = total_mood_value / total_entries
    else:
        average_mood = 0

    return render_template('index.html', total_entries=total_entries, average_mood=average_mood)

@app.route('/tracker', methods=['GET', 'POST'])
def tracker():
    if request.method == 'POST':
        date = request.form['date']
        mood = request.form['mood']
        notes = request.form['notes']
        if mood:  # Basic validation
            new_entry = MoodEntry(date=date, mood=mood, notes=notes)
            db.session.add(new_entry)
            db.session.commit()
            return redirect(url_for('tracker'))
    entries = MoodEntry.query.all()
    return render_template('tracker.html', entries=entries)

@app.route('/edit_entry/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    entry = MoodEntry.query.get_or_404(entry_id)
    if request.method == 'POST':
        entry.date = request.form['date']
        entry.mood = request.form['mood']
        entry.notes = request.form['notes']
        db.session.commit()
        return redirect(url_for('tracker'))
    return render_template('edit_entry.html', entry=entry)

@app.route('/delete_entry/<int:entry_id>', methods=['GET'])
def delete_entry(entry_id):
    entry = MoodEntry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('tracker'))

if __name__ == '__main__':
    app.run(debug=True)