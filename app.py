import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session
from aws.dynamodb_utils import check_login

app = Flask(__name__)
app.secret_key = 'your-secret-key'

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        print(f"🔍 Received: {email=}, {password=}")  # Debug print

        user = check_login(email, password)
        print(f"📦 check_login returned: {user}")  # Debug print

        if user:
            session['user_name'] = user['user_name']
            print("✅ Login successful!")
            return redirect(url_for('main'))
        else:
            print("❌ Invalid login credentials.")
            flash("Invalid email or password")
            return redirect(url_for('login'))

    return render_template('login.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        url = "https://m0uoz68yl6.execute-api.us-east-1.amazonaws.com/dev/register"
        response = requests.post(url, json={
            "email": email,
            "user_name": username,
            "password": password
        })

        if response.status_code == 200:
            flash("Registered successfully! Please login.", "success")
            return redirect(url_for('login'))
        elif response.status_code == 409:
            flash("The email already exists", "warning")
        else:
            flash("Something went wrong. Please try again.", "danger")

    return render_template('register.html')

@app.route('/unsubscribe', methods=['GET', 'POST'])
def unsubscribe():
    if request.method == 'POST':
        email = request.form['email']
        song = request.form['song']

        url = "https://m0uoz68yl6.execute-api.us-east-1.amazonaws.com/dev/unsubscribe"

        payload = {
            "email": email,
            "song": song
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            flash("Unsubscribed successfully!", "success")
        elif response.status_code == 404:
            flash("Subscription not found.", "warning")
        else:
            flash("Unsubscription failed. Try again.", "danger")

        return redirect(url_for('unsubscribe'))

    return render_template('unsubscribe.html')

@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    if request.method == 'POST':
        email = request.form['email']
        song = request.form['song']

        url = "https://m0uoz68yl6.execute-api.us-east-1.amazonaws.com/dev/subscribe"

        payload = {
            "email": email,
            "song": song
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            flash("Subscribed successfully!", "success")
        elif response.status_code == 409:
            flash("Already subscribed.", "warning")
        elif response.status_code == 404:
            flash("Song does not exist.", "warning")
        else:
            flash("Subscription failed. Try again.", "danger")

        return redirect(url_for('subscribe'))

    return render_template('subscribe.html')

@app.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    email = request.args.get('email')
    if not email:
        return "Email is required", 400

    url = "https://m0uoz68yl6.execute-api.us-east-1.amazonaws.com/dev/subscriptions"
    try:
        response = requests.get(url, params={"email": email})
        if response.status_code == 200:
            data = response.json()
            return render_template('subscriptions.html', songs=data.get('subscriptions', []))
        else:
            flash("Error retrieving subscriptions", "danger")
            return redirect(url_for('main'))
    except requests.RequestException:
        flash("Unable to connect to subscriptions API", "danger")
        return redirect(url_for('main'))

@app.route('/main')
def main():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    return render_template('main.html', user_name=session['user_name'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=True)
