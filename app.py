from flask import Flask, render_template, request, redirect, url_for, flash, session
from utilities.dynamoDb_utils import check_login, register_user, search_music  # Ensure these functions exist
from utilities.s3_utils import get_presigned_url

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure key or use environment variables

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

    # For demonstration, subscriptions are not implemented yet; pass an empty list.
    subscriptions = []
    results = []

    # Handle search form submission
    if request.method == 'POST':
        # Get search criteria from the form
        criteria = {
            'title': request.form.get('title', ''),
            'artist': request.form.get('artist', ''),
            'album': request.form.get('album', ''),
            'year': request.form.get('year', '')
        }
        # Call search_music utility (should be implemented to search your music table)
        results = search_music(criteria)
        # For each search result, if an s3_key is available, generate a pre-signed URL.
        for res in results:
            if 's3_key' in res:
                res['image_url'] = get_presigned_url(res['s3_key'])

    return render_template('main.html', user_name=session['user_name'], subscriptions=subscriptions, results=results)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
