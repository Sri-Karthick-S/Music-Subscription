# Advanced Task Progress - Nithyashree KP

## ✅ Step 1: Login via Lambda + API Gateway

- Created `checkLogin` Lambda function in AWS
- Connected it to API Gateway via a `/login` GET endpoint
- Created a DynamoDB table named `login` and added a test user
- Replaced Flask’s `check_login()` with a `requests.get()` call to the deployed API
- Successfully logged in through Flask using Lambda response
- Pushed changes to GitHub ✅

## 📝 Notes

- API URL used:  
  `https://m0uoz68yl6.execute-api.us-east-1.amazonaws.com/dev/login`
- Table: `login`
- Test credentials:
  - Email: `test@example.com`
  - Password: `123`

---

Next: Create `registerUser` Lambda for the `/register` endpoint.
