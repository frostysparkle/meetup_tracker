---
title: Meetup Tracker API
emoji: 🎟️
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🎟️ Meetup Tracker

A full-stack attendance tracking system for meetups. This project provides a Flask-based backend for managing attendees and tickets, and a Streamlit-based frontend for scanning QR codes at the event.

## 🚀 Features

- **Attendee Management**: API to register new attendees and generate unique tickets.
- **QR Code Generation**: Automatically generates a unique QR code for each registered attendee.
- **Email Delivery**: Sends tickets directly to attendees' emails using SMTP.
- **QR Scanner**: Mobile-friendly Streamlit interface to scan tickets using the device camera.
- **Real-time Stats**: Dashboard showing live attendance counts.
- **Secure Access**: Admin and App-level token authentication.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Flask-SQLAlchemy (SQLite)
- **Frontend**: Streamlit, OpenCV (for QR scanning)
- **Deployment**: Docker, Render/Hugging Face Spaces
- **Utilities**: `qrcode` for generation, `smtplib` for emails

## 📦 Project Structure

```text
├── app.py              # Streamlit Frontend application
├── wsgi.py             # Flask Backend entry point
├── backend/            # Backend package
│   ├── models.py       # SQLAlchemy Database models
│   ├── routes/         # API endpoints
│   └── utils/          # Email and QR utilities
├── requirements.txt    # Full dependencies (Frontend + Backend)
└── requirements-backend.txt # Minimal backend dependencies
```

## ⚙️ Setup & Installation

### 1. Environment Variables

Create a `.env` file (for backend) or use secrets management for the following variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ADMIN_TOKEN` | Secret for administrative actions (e.g., adding users) | (Required) |
| `APP_PASSWORD` | Password for Streamlit login and API access | (Required) |
| `SMTP_EMAIL` | Sender email address for tickets | - |
| `SMTP_PASSWORD` | App-specific password for the sender email | - |
| `API_BASE_URL` | URL where the backend is hosted | `http://localhost:5000/api` |

### 2. Backend Setup

```bash
# Install dependencies
pip install -r requirements-backend.txt

# Run the backend
python wsgi.py
```

*Note: On first run, you may need to initialize the database:*
```python
from backend import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
```

### 3. Frontend Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

## 🚢 Deployment

### Docker
The included `Dockerfile` is optimized for running the backend on platforms like Hugging Face Spaces.

### Render
Use the `render.yaml` file to deploy the backend as a Web Service on Render.

---
Built with ❤️ for the IITM BS Community.
