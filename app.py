import streamlit as st
import threading
import os
import sys
import requests
import cv2
import numpy as np
import time

# Ensure the parent directory is in the path to import backend modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend import create_app
from backend.models import db

API_BASE_URL = "http://localhost:5000/api"

# Page Config
st.set_page_config(page_title="Meetup Tracker", layout="wide")

# 1. Background Flask Server
@st.cache_resource
def run_flask_app():
    app = create_app()
    with app.app_context():
        # Initialize DB on start
        db.create_all()
        print("Database initialized.")
        
    def _run():
        app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=False)
        
    thread = threading.Thread(target=_run)
    thread.daemon = True
    thread.start()
    
    # Wait a tiny bit for the server to start
    time.sleep(1)
    return thread

run_flask_app()

# 2. Streamlit Frontend

# Initialize session state
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

def fetch_stats():
    try:
        response = requests.get(f"{API_BASE_URL}/stats")
        if response.status_code == 200:
            return response.json().get('total_present', 0)
    except Exception as e:
        pass
    return 0

if not st.session_state['auth']:
    st.title("Admin Login")
    with st.form("login_form"):
        password = st.text_input("Enter APP_PASSWORD", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            try:
                response = requests.post(f"{API_BASE_URL}/verify_password", json={"password": password})
                if response.status_code == 200 and response.json().get("success"):
                    st.session_state['auth'] = True
                    st.rerun()
                else:
                    st.error("Invalid password")
            except Exception as e:
                st.error(f"Error connecting to server: {e}")
else:
    # Authenticated UI
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("Meetup Tracker")
    with col2:
        st.metric("Total Present", fetch_stats())
    with col3:
        if st.button("Logout"):
            st.session_state['auth'] = False
            st.rerun()

    tab1, tab2 = st.tabs(["Scanner", "Attendees"])

    with tab1:
        st.header("Scan Ticket QR Code")
        st.write("Use your device's camera to scan the QR code.")
        
        img_file_buffer = st.camera_input("Take a picture of the QR code")
        
        if img_file_buffer is not None:
            # Read the image
            bytes_data = img_file_buffer.getvalue()
            cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
            
            # Detect QR code
            detector = cv2.QRCodeDetector()
            data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)
            
            if data:
                st.success("QR Code detected successfully!")
                try:
                    response = requests.post(f"{API_BASE_URL}/mark_present", json={"id": data})
                    if response.status_code == 200:
                        st.success(response.json().get("message"))
                    else:
                        st.error(response.json().get("error", "Unknown error"))
                except Exception as e:
                    st.error(f"Failed to connect to API: {e}")
            else:
                st.warning("No QR code found in the image. Please try again and ensure the code is clear.")

    with tab2:
        st.header("Present Attendees")
        if st.button("Refresh List"):
            st.rerun()
            
        try:
            response = requests.get(f"{API_BASE_URL}/attendees")
            if response.status_code == 200:
                attendees = response.json()
                if attendees:
                    st.dataframe(attendees, use_container_width=True)
                else:
                    st.info("No attendees present yet.")
            else:
                st.error("Failed to load attendees.")
        except Exception as e:
            st.error(f"Error connecting to server: {e}")
