from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages
from utilities.dynamoDb_utils import check_login, register_user, search_music, get_user_subscriptions, subscribe_song, remove_subscription
from utilities.s3_utils import get_presigned_url

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key or use environment variables

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any leftover flash messages
    get_flashed_messages()  # This will remove any pending flash messages

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = check_login(email, password)
        if user:
            session['user_email'] = user['email']
            session['user_name'] = user.get('user_name', '')
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
        elif result == "success":
            flash("Registered successfully! Please login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Registration failed. Please try again.", "danger")
    return render_template('register.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    # Retrieve subscriptions for the logged-in user (strongly consistent read if needed)
    subscriptions = get_user_subscriptions(session['user_email'])
    # Generate S3 pre-signed URLs for the subscription images
    for sub in subscriptions:
        if 's3_key' in sub and sub['s3_key']:
            sub['image_url'] = get_presigned_url(sub['s3_key'])

    results = []
    query_performed = False
    if request.method == 'POST' and 'title' in request.form:
        query_performed = True
        # Get search criteria from the form
        criteria = {
            'title': request.form.get('title', ''),
            'artist': request.form.get('artist', ''),
            'album': request.form.get('album', ''),
            'year': request.form.get('year', '')
        }
        results = search_music(criteria)
        # For each search result, generate a pre-signed URL and mark as subscribed if already in subscriptions
        for res in results:
            if 's3_key' in res and res['s3_key']:
                res['image_url'] = get_presigned_url(res['s3_key'])
            # Compute unique song identifier (assuming song_id equals title_album)
            title_album = res.get('title_album')
            res['subscribed'] = any(sub['title_album'] == title_album for sub in subscriptions)

    return render_template('main.html', user_name=session['user_name'],
                           subscriptions=subscriptions, results=results, query_performed=query_performed)

@app.route('/subscribe', methods=['POST'])
def subscribe():
    if 'user_email' not in session:
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))
    user_email = session['user_email']
    # Use form data instead of JSON
    song_data = {
        'title_album': request.form.get('title_album'),
        'title': request.form.get('title'),
        'artist': request.form.get('artist'),
        'album': request.form.get('album'),
        'year': request.form.get('year'),
        's3_key': request.form.get('s3_key')
    }
    if subscribe_song(user_email, song_data):
        flash("Subscribed successfully", "success")
    else:
        flash("Subscription failed", "danger")
    return redirect(url_for('main'))

@app.route('/remove_subscription', methods=['POST'])
def remove_subscription_route():
    if 'user_email' not in session:
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))
    user_email = session['user_email']
    title_album = request.form.get('title_album')
    if remove_subscription(user_email, title_album):
        flash("Subscription removed", "success")
    else:
        flash("Failed to remove subscription", "danger")
    return redirect(url_for('main'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)
