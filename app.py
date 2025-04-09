from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages
from utilities.dynamoDb_utils import (
    check_login,
    register_user,
    email_exists,
    search_music,
    get_user_subscriptions,
    subscribe_song,
    remove_subscription,
    login_table  
)
from utilities.s3_utils import get_presigned_url
import re
from botocore.exceptions import ClientError

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key or use environment variables

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear previous flash messages
    get_flashed_messages()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # ✅ Validate RMIT student email format
        pattern = r'^s\d{7,8}@student\.rmit\.edu\.au$'
        if not re.match(pattern, email):
            flash("Invalid RMIT student email format.", "login-danger")
            return render_template('auth.html', form_type='login')

        # ✅ Check login from DynamoDB
        user = check_login(email, password)
        if user:
            session['user_email'] = user['email']
            session['user_name'] = user.get('user_name', '')
            return redirect(url_for('main'))
        else:
            flash("Email or password is incorrect.", "login-danger")
            return render_template('auth.html', form_type='login')

    return render_template('auth.html', form_type='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # Email format check
        if not re.match(r'^s\d{7,8}@student\.rmit\.edu\.au$', email):
            flash("❌ Invalid email format. Must be RMIT student email.", "register-danger")
            return render_template('auth.html', form_type='register')

        # Username format check
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]{2,}$', username):
            flash("❌ Username must start with a letter.", "register-danger")
            return render_template('auth.html', form_type='register')

        # Password strength check
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{6,12}$', password):
            flash("❌ Password must be 6–12 characters with upper, lower, digit & special char.", "register-danger")
            return render_template('auth.html', form_type='register')

        # ✅ Check if email already exists in DynamoDB
        try:
            if email_exists(email):
                flash(" Email already exists.", "register-danger")
                return render_template("auth.html", form_type="register")
        except ClientError as e:
            print("DynamoDB error:", e.response['Error']['Message'])
            flash("❌ Internal error while checking email.", "register-danger")
            return render_template('auth.html', form_type='register')

        # ✅ Add new user (email is unique)
        try:
            login_table.put_item(Item={
                'email': email,
                'user_name': username,
                'password': password
            })
            flash("✅ Registered successfully! Please login.", "register-success")
            return redirect(url_for('login'))
        except ClientError as e:
            print("PutItem error:", e.response['Error']['Message'])
            flash("❌ Failed to register user. Try again.", "register-danger")

    
    flash("✅ Registered successfully! Please login.", "register-success")
    return render_template('auth.html', form_type='register')
@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    subscriptions = get_user_subscriptions(session['user_email'])
    for sub in subscriptions:
        if 's3_key' in sub and sub['s3_key']:
            sub['image_url'] = get_presigned_url(sub['s3_key'])

    results = []
    query_performed = False

    if request.method == 'POST':
        criteria = {
            'title': request.form.get('title', ''),
            'artist': request.form.get('artist', ''),
            'album': request.form.get('album', ''),
            'year': request.form.get('year', '')
        }
        session['last_search'] = criteria  # Store for reuse
        results = search_music(criteria)
        query_performed = True
    elif 'last_search' in session:
        criteria = session['last_search']
        results = search_music(criteria)
        query_performed = True

    for res in results:
        if 's3_key' in res and res['s3_key']:
            res['image_url'] = get_presigned_url(res['s3_key'])
        title_album = res.get('title_album')
        res['subscribed'] = any(sub['title_album'] == title_album for sub in subscriptions)

    return render_template('main.html',
                           user_name=session['user_name'],
                           subscriptions=subscriptions,
                           results=results,
                           query_performed=query_performed)

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
