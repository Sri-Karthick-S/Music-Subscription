from flask import Flask, render_template, request, redirect, url_for, flash, session
import boto3
from aws.dynamodb_utils import check_login, register_user, get_subscriptions, add_subscription, remove_subscription, search_music

app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = check_login(email, password)
        if user:
            session['user_name'] = user['user_name']
            session['email'] = email
            return redirect(url_for('main'))
        else:
            flash("Email or password is invalid", "danger")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        result = register_user(email, username, password)
        if result == "exists":
            flash("The email already exists", "warning")
        else:
            flash("Registered successfully! Please login.", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/main')
def main():
    subscriptions = get_subscriptions(session['email'])
    subscribed_titles = {
        (s['title'].lower(), s['artist'].lower(), s['album'].lower())
        for s in subscriptions
    }
    return render_template(
        'main.html',
        user_name=session['user_name'],
        subscriptions=subscriptions,
        results=[],
        subscribed_titles=subscribed_titles
    )

@app.route('/subscribe', methods=['POST'])
def subscribe():
    song_data = {
        'title': request.form['title'],
        'album': request.form['album'],
        'artist': request.form['artist'],
        'year': request.form['year'],
        'image_url': request.form['image_url']
    }
    result = add_subscription(session['email'], song_data)
    flash(f"'{song_data['title']}' has been subscribed.", "success")
    return redirect(url_for('main'))

@app.route('/remove', methods=['POST'])
def remove():
    title = request.form['title']
    album = request.form['album']
    remove_subscription(session['email'], title, album)
    flash(f"'{title}' has been removed from your subscriptions.", "warning")
    return redirect(url_for('main'))

@app.route('/query', methods=['POST'])
def query_music():
    if 'email' not in session or 'user_name' not in session:
        return redirect(url_for('login'))

    filters = {
        'title': request.form.get('title'),
        'artist': request.form.get('artist'),
        'year': request.form.get('year'),
        'album': request.form.get('album')
    }

    results = search_music(filters)
    subscriptions = get_subscriptions(session['email'])

    # Create a set of (title, artist, album) for comparison
    subscribed_titles = {
        (s['title'].lower(), s['artist'].lower(), s['album'].lower())
        for s in subscriptions
    }

    return render_template(
        'main.html',
        user_name=session['user_name'],
        subscriptions=subscriptions,
        results=results,
        subscribed_titles=subscribed_titles
    )

if __name__ == '__main__':
    app.run(debug=True)
