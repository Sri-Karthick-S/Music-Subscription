from flask import Flask, render_template, request, redirect, url_for, flash, session, get_flashed_messages
import requests
# Import DynamoDB and S3 helper functions.
from utilities.dynamoDb_utils import check_login, search_music, get_user_subscriptions
from utilities.s3_utils import get_presigned_url


app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key or use environment variables

# ---------------------------------------------------------------
# HOME ROUTE: Redirect to login page.
# ---------------------------------------------------------------
@app.route('/')
def home():
    return redirect(url_for('login'))
# ---------------------------------------------------------------
# LOGIN ROUTE:
# - Uses direct DynamoDB interaction via check_login (Flask handles login directly).
# - Clears any pending flash messages.
# ---------------------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Clear any leftover flash messages
    get_flashed_messages()

    if request.method == 'POST':
        # Retrieve user credentials from the form.
        email = request.form['email']
        password = request.form['password']

        # Call a helper function that directly accesses DynamoDB to check credentials.
        user = check_login(email, password)
        if user:
            # Set session variables if login is successful.
            session['user_email'] = user['email']
            session['user_name'] = user.get('user_name', '')
            return redirect(url_for('main'))
        else:
            flash("Email or password is invalid", "danger")
    # Render the login template.
    return render_template('login.html')

# ---------------------------------------------------------------
# REGISTER ROUTE:
# - Uses API Gateway (and Lambda) to perform registration.
# - Validates and sends the registration data to the remote API.
# ---------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve registration details from the form.
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        # Construct the payload with an action parameter.
        payload = {
            "action": "register",
            "email": email,
            "username": username,
            "password": password
        }

        try:
            # Make a POST request to the API Gateway endpoint for registration.
            r = requests.post("https://jq2rcrhjsd.execute-api.us-east-1.amazonaws.com/Production/register", json=payload)
            if r.status_code == 200:
                flash("Registered successfully! Please login.", "success")
                return redirect(url_for('login'))
            elif r.status_code == 409:
                # 409 indicates conflict (user already exists).
                flash("The email already exists, please try login", "warning")
            else:
                # Other errors, display the message from the response.
                flash(r.json()['message'], "warning")
        except Exception:
            flash("Error registering. Backend unreachable.", "danger")
    # Render the register template.
    return render_template('register.html')
# ---------------------------------------------------------------
# MAIN ROUTE:
# - Checks if the user is logged in (session).
# - Retrieves subscriptions directly from DynamoDB via get_user_subscriptions.
# - If a search is performed (post with 'title' field), it calls search_music.
# - Generates S3 pre-signed URLs for images.
# ---------------------------------------------------------------
@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    # Retrieve subscriptions for the logged-in user
    subscriptions = get_user_subscriptions(session['user_email'])
    # Generate S3 pre-signed URLs for the subscription images
    for sub in subscriptions:
        if 's3_key' in sub and sub['s3_key']:
            sub['image_url'] = get_presigned_url(sub['s3_key'])

    results = []
    query_performed = False
    # If a search is triggered (POST method containing 'title'-trigger), proceed with searching.
    if request.method == 'POST' and 'title' in request.form:
        query_performed = True
        # Get search criteria from the form
        criteria = {
            'title': request.form.get('title', ''),
            'artist': request.form.get('artist', ''),
            'album': request.form.get('album', ''),
            'year': request.form.get('year', '')
        }
        # Verify that at least one field is filled.
        if not (criteria['title'] or criteria['artist'] or criteria['album'] or criteria['year']):
            flash("Please fill in at least one field to query.", "warning")
            return redirect(url_for('main'))

        # Call search_music from DynamoDB (for search, direct db call).
        results = search_music(criteria)
        # For each search result, generate a pre-signed URL and mark as subscribed if already in subscriptions
        for res in results:
            if 's3_key' in res and res['s3_key']:
                res['image_url'] = get_presigned_url(res['s3_key'])
            # Compute unique song identifier
            title_album = res.get('title_album')
            res['subscribed'] = any(sub['title_album'] == title_album for sub in subscriptions)

    return render_template('main.html', user_name=session['user_name'],
                           subscriptions=subscriptions, results=results, query_performed=query_performed)
# ---------------------------------------------------------------
# SUBSCRIBE ROUTE:
# - Uses API Gateway for subscribing.
# - Constructs a payload (with action 'subscribe') and sends it to the API.
# ---------------------------------------------------------------
@app.route('/subscribe', methods=['POST'])
def subscribe():
    if 'user_email' not in session:
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))
    # Build the song subscription data from form inputs.
    song_data = {
        'action': 'subscribe',
        'email': session['user_email'],
        'title_album': request.form.get('title_album'),
        'title': request.form.get('title'),
        'artist': request.form.get('artist'),
        'album': request.form.get('album'),
        'year': request.form.get('year'),
        's3_key': request.form.get('s3_key')
    }

    try:
        r = requests.post("https://jq2rcrhjsd.execute-api.us-east-1.amazonaws.com/Production/subscribe", json=song_data)
        print("Response code:", r.status_code)
        if r.status_code == 200:
            flash("Subscribed successfully", "success")
        else:
            flash(r.json()['message'], "danger")
    except Exception:
        flash("Subscription failed. Backend unreachable.", "danger")
    return redirect(url_for('main'))

# ---------------------------------------------------------------
# REMOVE SUBSCRIPTION ROUTE:
# - Uses API Gateway for removing a subscription.
# - Constructs a payload (with action 'remove_subscription') and sends it to the API.
# ---------------------------------------------------------------
@app.route('/remove_subscription', methods=['POST'])
def remove_subscription_route():
    if 'user_email' not in session:
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))
    user_email = session['user_email']
    title_album = request.form.get('title_album')

    payload = {
        'action': 'remove_subscription',
        'email': session['user_email'],
        'title_album': request.form.get('title_album')
    }

    try:
        r = requests.post("https://jq2rcrhjsd.execute-api.us-east-1.amazonaws.com/Production/remove_subscription", json=payload)
        if r.status_code == 200:
            flash("Subscription removed", "success")
        else:
            flash(r.json()['message'], "danger")
    except Exception:
        flash("Removal failed. Backend unreachable.", "danger")
    return redirect(url_for('main'))

# ---------------------------------------------------------------
# LOGOUT ROUTE:
# - Clears the user session and redirects to login.
# ---------------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------------------------------------------------
# AFTER REQUEST HANDLER:
# - Adds headers to disable caching in the browser.
# ---------------------------------------------------------------
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ---------------------------------------------------------------
# MAIN ENTRY POINT:
# - Runs the Flask development server when executed directly.
# ---------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
