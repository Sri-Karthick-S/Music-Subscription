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
import requests


app = Flask(__name__)
app.secret_key = 'your-secret-key'  

@app.route('/')
def home():
    return redirect(url_for('login'))


login_API= "https://wir5etx69g.execute-api.us-east-1.amazonaws.com/dev_user_login"
@app.route('/login', methods=['GET', 'POST'])
def login():
    # get_flashed_messages()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Validate email
        if not re.match(r'^s\d{7,8}@student\.rmit\.edu\.au$', email):
            flash("Invalid RMIT student email format.", "login-danger")
            return render_template('auth.html', form_type='login', email='')

        # ✅ Call Lambda through API Gateway
        try:
            response = requests.post(
                f"{login_API}/login",
                json={'email': email, 'password': password},
                timeout=5
            )
            if response.status_code == 200:
                user = response.json()
                session['user_email'] = user['email']
                session['user_name'] = user.get('user_name', '')
                return redirect(url_for('main'))
            elif response.status_code == 401:
                flash("Incorrect password.", "login-danger")
            elif response.status_code == 404:
                flash("User not found.", "login-danger")
            elif response.status_code == 400:
                flash("Missing email or password.", "login-danger")
            else:
                flash("Login failed due to server error.", "login-danger")

        except requests.exceptions.RequestException as e:
            print("Login API failed:", e)
            flash("Could not connect to login service.", "login-danger")

    return render_template('auth.html', form_type='login', email='')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Clear previous flash messages
#     get_flashed_messages()

#     if request.method == 'POST':
#         email = request.form.get('email', '').strip()
#         password = request.form.get('password', '').strip()

#         # ✅ Validate RMIT student email format
#         pattern = r'^s\d{7,8}@student\.rmit\.edu\.au$'
#         if not re.match(pattern, email):
#             flash("Invalid RMIT student email format.", "login-danger")
#             return render_template('auth.html', form_type='login')

#         # ✅ Check login from DynamoDB
#         user = check_login(email, password)
#         if user:
#             session['user_email'] = user['email']
#             session['user_name'] = user.get('user_name', '')
#             return redirect(url_for('main'))
#         else:
#             flash("Email or password is incorrect.", "login-danger")
#             return render_template('auth.html', form_type='login')

#     return render_template('auth.html', form_type='login')
registter_API="https://b3sckbrua9.execute-api.us-east-1.amazonaws.com/dev_user_register"
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # ✅ 1. Validate Email
        if not re.match(r'^s\d{7,8}@student\.rmit\.edu\.au$', email):
            flash("❌ Invalid email format. Must be RMIT student email.", "register-danger")
            return render_template('auth.html', form_type='register')

        # ✅ 2. Validate Username
        if not re.match(r'^[A-Za-z][A-Za-z0-9_]{2,}$', username):
            flash("❌ Username must start with a letter.", "register-danger")
            return render_template('auth.html', form_type='register')

        # ✅ 3. Validate Password
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{6,12}$', password):
            flash("❌ Password must be 6–12 characters with upper, lower, digit & special char.", "register-danger")
            return render_template('auth.html', form_type='register')

        # ✅ 4. Call API Gateway to trigger Lambda for registration
        try:
            response = requests.post(
                f"{registter_API}/register",
                json={
                    "email": email,
                    "username": username,
                    "password": password
                },
                timeout=5
            )
            print("a")
            print(response)
            if response.status_code == 201:
                flash("✅ Registered successfully! Please login.", "login-sucess")
                return redirect(url_for('login'))

            elif response.status_code == 409:
                flash("⚠️ Email already exists. Please login or use another.", "register-danger")
            else:
                flash("❌ Registration failed. Server error.", "register-danger")

        except requests.exceptions.RequestException as e:
            print("API call failed:", e)
            flash("❌ Could not reach registration service. Try again later.", "register-danger")

    return render_template('auth.html', form_type='register')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         email = request.form['email'].strip()
#         username = request.form['username'].strip()
#         password = request.form['password'].strip()

#         # Email format check
#         if not re.match(r'^s\d{7,8}@student\.rmit\.edu\.au$', email):
#             flash("❌ Invalid email format. Must be RMIT student email.", "register-danger")
#             return render_template('auth.html', form_type='register')

#         # Username format check
#         if not re.match(r'^[A-Za-z][A-Za-z0-9_]{2,}$', username):
#             flash("❌ Username must start with a letter.", "register-danger")
#             return render_template('auth.html', form_type='register')

#         # Password strength check
#         if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{6,12}$', password):
#             flash("❌ Password must be 6–12 characters with upper, lower, digit & special char.", "register-danger")
#             return render_template('auth.html', form_type='register')

#         # ✅ Check if email already exists in DynamoDB
#         try:
#             if email_exists(email):
#                 flash(" Email already exists.", "register-danger")
#                 return render_template("auth.html", form_type="register")
#         except ClientError as e:
#             print("DynamoDB error:", e.response['Error']['Message'])
#             flash("❌ Internal error while checking email.", "register-danger")
#             return render_template('auth.html', form_type='register')

#         # ✅ Add new user (email is unique)
#         try:
#             login_table.put_item(Item={
#                 'email': email,
#                 'user_name': username,
#                 'password': password
#             })
#             flash("✅ Registered successfully! Please login.", "register-success")
#             return redirect(url_for('login'))
#         except ClientError as e:
#             print("PutItem error:", e.response['Error']['Message'])
#             flash("❌ Failed to register user. Try again.", "register-danger")

    
#     flash("✅ Registered successfully! Please login.", "register-success")
#     return render_template('auth.html', form_type='register')

SEARCH_API = "https://0433e01uuc.execute-api.us-east-1.amazonaws.com/dev_main/search"
GET_SUBS_API = "https://0433e01uuc.execute-api.us-east-1.amazonaws.com/dev_main/subscriptions"


@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_email' not in session:
        return redirect(url_for('login'))

    user_email = session['user_email']
    user_name = session.get('user_name', '')

    # Fetch subscriptions
    subscriptions = []
    try:
        resp = requests.post(GET_SUBS_API, json={"email": user_email}, timeout=5)
        if resp.status_code == 200:
            subscriptions = resp.json()
            # Attach image URLs to subscriptions
            for sub in subscriptions:
                if 's3_key' in sub and sub['s3_key']:
                    sub['image_url'] = get_presigned_url(sub['s3_key'])
    except Exception as e:
        print("Subscription API error:", e)

    results = []
    query_performed = False

    if request.method == 'POST':
        # Get form values
        criteria = {
            'title': request.form.get('title', '').strip(),
            'artist': request.form.get('artist', '').strip(),
            'album': request.form.get('album', '').strip(),
            'year': request.form.get('year', '').strip()
        }

        # If all fields empty
        if not any(criteria.values()):
            flash("⚠️ Enter at least one value for Query", "query-warning")
            return render_template('main.html',
                                   user_name=user_name,
                                   subscriptions=subscriptions,
                                   results=[],
                                   query_performed=False)

        session['last_search'] = criteria

        # Perform search
        try:
            res = requests.post(SEARCH_API, json=criteria, timeout=5)
            if res.status_code == 200:
                results = res.json()
                query_performed = True
        except Exception as e:
            print("Search API error:", e)

    elif 'last_search' in session:
        try:
            res = requests.post(SEARCH_API, json=session['last_search'], timeout=5)
            if res.status_code == 200:
                results = res.json()
                query_performed = True
        except Exception as e:
            print("Search API error:", e)

    # Attach images and mark subscription status
    for res in results:
        if 's3_key' in res and res['s3_key']:
            res['image_url'] = get_presigned_url(res['s3_key'])
        res['subscribed'] = any(sub['title_album'] == res.get('title_album') for sub in subscriptions)

    return render_template('main.html',
                           user_name=user_name,
                           subscriptions=subscriptions,
                           results=results,
                           query_performed=query_performed)


# @app.route('/main', methods=['GET', 'POST'])
# def main():
#     if 'user_email' not in session:
#         return redirect(url_for('login'))

#     subscriptions = get_user_subscriptions(session['user_email'])
#     for sub in subscriptions:
#         if 's3_key' in sub and sub['s3_key']:
#             sub['image_url'] = get_presigned_url(sub['s3_key'])

#     results = []
#     query_performed = False

#     if request.method == 'POST':
#         criteria = {
#             'title': request.form.get('title', ''),
#             'artist': request.form.get('artist', ''),
#             'album': request.form.get('album', ''),
#             'year': request.form.get('year', '')
#         }
#         session['last_search'] = criteria  # Store for reuse
#         results = search_music(criteria)
#         query_performed = True
#     elif 'last_search' in session:
#         criteria = session['last_search']
#         results = search_music(criteria)
#         query_performed = True

#     for res in results:
#         if 's3_key' in res and res['s3_key']:
#             res['image_url'] = get_presigned_url(res['s3_key'])
#         title_album = res.get('title_album')
#         res['subscribed'] = any(sub['title_album'] == title_album for sub in subscriptions)

#     return render_template('main.html',
#                            user_name=session['user_name'],
#                            subscriptions=subscriptions,
#                            results=results,
#                            query_performed=query_performed)




SUBSCRIBE_API = "https://i5fbktqbg0.execute-api.us-east-1.amazonaws.com/dev_subscribe/subscribe"
@app.route('/subscribe', methods=['POST'])
def subscribe():
    if 'user_email' not in session:
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))

    user_email = session['user_email']

    song_data = {
        'email': user_email,
        'title_album': request.form.get('title_album'),
        'title': request.form.get('title'),
        'artist': request.form.get('artist'),
        'album': request.form.get('album'),
        'year': request.form.get('year'),
        's3_key': request.form.get('s3_key')
    }
    try:
        response = requests.post(SUBSCRIBE_API, json=song_data, timeout=5)
        if response.status_code == 201:
            flash("✅ Subscribed successfully", "success")
        else:
            flash("❌ Subscription failed", "danger")
    except requests.RequestException as e:
        print("Subscription API error:", e)
        flash("❌ Error subscribing to song", "danger")

    return redirect(url_for('main'))

# @app.route('/subscribe', methods=['POST'])
# def subscribe():
#     if 'user_email' not in session:
#         flash("Unauthorized access", "danger")
#         return redirect(url_for('login'))
#     user_email = session['user_email']
#     # Use form data instead of JSON
#     song_data = {
#         'title_album': request.form.get('title_album'),
#         'title': request.form.get('title'),
#         'artist': request.form.get('artist'),
#         'album': request.form.get('album'),
#         'year': request.form.get('year'),
#         's3_key': request.form.get('s3_key')
#     }
#     if subscribe_song(user_email, song_data):
#         flash("Subscribed successfully", "success")
#     else:
#         flash("Subscription failed", "danger")
#     return redirect(url_for('main'))


UNSUBSCRIBE_API = "https://i5fbktqbg0.execute-api.us-east-1.amazonaws.com/dev_subscribe/unsubscribe"
@app.route('/remove_subscription', methods=['POST'])
def remove_subscription_route():
    if 'user_email' not in session:
        flash("Unauthorized access", "danger")
        return redirect(url_for('login'))

    user_email = session['user_email']
    title_album = request.form.get('title_album')

    print("🧪 Unsubscribe POST ->", user_email, title_album)

    try:
        response = requests.post(UNSUBSCRIBE_API, json={
            "email": user_email,
            "title_album": title_album
        }, timeout=5)

        print("🔁 Lambda Response:", response.status_code, response.text)

        if response.status_code == 200:
            flash("✅ Subscription removed", "success")
        else:
            flash("❌ Failed to remove subscription", "danger")
    except requests.RequestException as e:
        print("Unsubscribe API error:", e)
        flash("❌ Error removing subscription", "danger")

    return redirect(url_for('main'))

# @app.route('/remove_subscription', methods=['POST'])
# def remove_subscription_route():
#     if 'user_email' not in session:
#         flash("Unauthorized access", "danger")
#         return redirect(url_for('login'))
#     user_email = session['user_email']
#     title_album = request.form.get('title_album')
#     if remove_subscription(user_email, title_album):
#         flash("Subscription removed", "success")
#     else:
#         flash("Failed to remove subscription", "danger")
#     return redirect(url_for('main'))

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
