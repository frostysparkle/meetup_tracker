import streamlit as st
import threading
import os
import sys
import streamlit.components.v1 as components

# Ensure the parent directory is in the path to import backend modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend import create_app
from backend.models import db

# Page Config
st.set_page_config(page_title="Meetup Tracker", layout="wide", initial_sidebar_state="collapsed")

# 1. Background Flask Server
@st.cache_resource
def run_flask_app():
    app = create_app()
    with app.app_context():
        # Initialize DB on start
        db.create_all()
        print("Database initialized.")
        
    def _run():
        # Run on a specific port, avoiding Streamlit's port
        app.run(host='0.0.0.0', port=5000, use_reloader=False, debug=False)
        
    thread = threading.Thread(target=_run)
    thread.daemon = True # Allows Streamlit to exit cleanly
    thread.start()
    return thread

# Start backend
run_flask_app()

# 2. Render Frontend
# We read the index.html and embed it. 
# We need to read it as a string and pass it to components.html
# Note: For relative paths in index.html to work correctly (like ./css/style.css),
# they might fail if served purely as a string blob.
# Alternatively, we can use an iframe if we served the static files via Flask.
# Let's serve the frontend via components.html by injecting the HTML content directly,
# but we need to inline the CSS/JS or serve them through Flask. 
# Since we have separate files, it's easier to serve the frontend folder as static files via Flask, 
# and point an iframe to it. Let's adjust the Flask app setup quickly here to serve the static folder.

frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')
app_url = "http://localhost:5000"

st.markdown("""
    <style>
        /* Hide Streamlit elements */
        .stApp header {display:none;}
        .stApp footer {display:none;}
    </style>
""", unsafe_allow_html=True)

# Actually, the best way to handle this robustly without changing backend too much 
# is to read the files and build a combined HTML string, or use Streamlit's static file serving.
# For simplicity and given the prompt constraints to use components.v1.html, let's embed an iframe
# but since the static files aren't served by Streamlit directly, we should have Flask serve them.

# Let's dynamically patch Flask app in this script to serve the frontend dir before starting it.
# We will just write a small helper to load the HTML with injected JS/CSS if needed.
# Since we already created separate files, reading and injecting is safest for components.html.

def get_injected_html():
    with open(os.path.join(frontend_path, 'index.html'), 'r') as f:
        html = f.read()
        
    # Replace relative paths with inline content or full paths if possible.
    # To keep it simple, let's read the CSS and JS and inject them into <style> and <script> tags.
    with open(os.path.join(frontend_path, 'css', 'style.css'), 'r') as f:
        css = f.read()
    
    js_files = [
        os.path.join(frontend_path, 'js', 'components', 'Navbar.js'),
        os.path.join(frontend_path, 'js', 'components', 'Login.js'),
        os.path.join(frontend_path, 'js', 'components', 'Scanner.js'),
        os.path.join(frontend_path, 'js', 'components', 'Attendees.js'),
        os.path.join(frontend_path, 'js', 'app.js')
    ]
    
    js_content = ""
    for js_f in js_files:
        with open(js_f, 'r') as f:
            js_content += f.read() + "\n"
            
    # Inject CSS
    html = html.replace('<link rel="stylesheet" href="./css/style.css">', f'<style>{css}</style>')
    
    # Remove script tags
    html = html.replace('<script src="./js/components/Navbar.js"></script>', '')
    html = html.replace('<script src="./js/components/Login.js"></script>', '')
    html = html.replace('<script src="./js/components/Scanner.js"></script>', '')
    html = html.replace('<script src="./js/components/Attendees.js"></script>', '')
    html = html.replace('<script src="./js/app.js"></script>', f'<script>{js_content}</script>')
    
    return html

html_content = get_injected_html()

# Render the application
components.html(html_content, height=800, scrolling=True)

