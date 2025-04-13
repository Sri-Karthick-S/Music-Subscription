# 🎵 Music Subscription Web Application

A cloud-based music app that allows users to register, log in, search for music, and subscribe to their favorite songs. Built using Flask and AWS services like EC2, S3, DynamoDB, Lambda, and API Gateway.

## 🖼️ User Interface

The application provides the following UI pages:
- `login.html` – Users can log in using registered credentials
- `register.html` – New users can sign up
- `main.html` – Main dashboard to search and subscribe to music

Snapshots:
- `loginpage.png`
- `registerpage.png`
- `mainpage.png`

---

## 🚀 Tech Stack

| Layer             | Technology                          |
|------------------|-------------------------------------|
| Frontend         | HTML, CSS, JavaScript               |
| Backend          | Python (Flask)                      |
| Cloud Services   | AWS EC2, S3, DynamoDB, Lambda, API Gateway |
| Deployment       | Apache + WSGI on EC2                |
| Package Manager  | pip (Python)                        |

---

## 📦 Features

- 🔐 User Registration and Login
- 🎧 Music Search and Subscription
- ☁️ Music & Image Storage on S3
- 🗃 Data managed via DynamoDB
- ⚙️ Lambda functions exposed via API Gateway
- 🌐 Deployed on EC2 with Apache and WSGI

---

## 🛠️ Local Setup Instructions

1. **Clone the repository**
```bash
git clone <repo-url>
cd Music-Subscription
