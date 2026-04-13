import streamlit as st
import os
import sys
import requests
import cv2
import numpy as np
import hashlib

# Page Config
st.set_page_config(page_title="Meetup Tracker", layout="wide")

try:
    API_BASE_URL = st.secrets["API_BASE_URL"]
except Exception:
    API_BASE_URL = "http://localhost:5000/api"

# Streamlit Frontend

def get_auth_token():
    try:
        app_pw = st.secrets["APP_PASSWORD"]
    except Exception:
        app_pw = "default_secret"
    return hashlib.sha256((app_pw + "_streamlit_salt").encode()).hexdigest()

expected_token = get_auth_token()

# Initialize session state
if 'auth' not in st.session_state:
    if "token" in st.query_params and st.query_params["token"] == expected_token:
        st.session_state['auth'] = True
    else:
        st.session_state['auth'] = False

def get_api_headers(app_pw_override=None):
    headers = {}
    
    # Hugging Face bypass header
    if "HF_TOKEN" in st.secrets:
        headers["Authorization"] = f"Bearer {st.secrets['HF_TOKEN']}"
        
    # Our internal app authentication header
    if app_pw_override:
        headers["X-App-Token"] = app_pw_override
    else:
        try:
            headers["X-App-Token"] = st.secrets["APP_PASSWORD"]
        except Exception:
            headers["X-App-Token"] = "default_secret"
            
    return headers

def fetch_stats():
    try:
        response = requests.get(f"{API_BASE_URL}/stats", headers=get_api_headers())
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
                    st.query_params["token"] = expected_token
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
            if "token" in st.query_params:
                del st.query_params["token"]
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
            response = requests.get(f"{API_BASE_URL}/attendees", headers=get_api_headers())
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
