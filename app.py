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
        email = request.form['email']
        password = request.form['password']
        user = check_login(email, password)  # ✅ Using boto3-based function
        if user:
            session['user_name'] = user['user_name']
            return redirect(url_for('main'))
        else:
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
